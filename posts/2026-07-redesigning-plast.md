# Re-designing Plast for more elegant solution

Over the last couple of weeks I have been working on my robotics communication framework in Zig. I finalized the core for the first version that I will publish, so I thought it's a good time to go work on something else for a couple of days so I don't burn out — the project was starting to feel boring. I'm very interested in Physical AI and robotics, so I decided to go back to `plast`, which is my simple deep learning framework written in `c` and `cuda`. I already implemented the cpu and gpu kernels for most of the tensor ops needed, built a tiny `JIT` compiler for it, and made python bindings so people can use it with an experiment tracking system. But there is something else. As someone interested in physical AI and robotics, this library is useless to me without the ability to do reinforcement learning with ease.

## Why rewrite in Zig?

I think this shouldn't be a shocker by now. I invested a good amount of time learning and writing Zig, and built glu from scratch in pure Zig. To be honest, writing python code for robots is not ideal — you don't get much control over your resources. And writing the api in c is not the most enjoyable experience you can get. So re-writing the core in Zig is a win. It's a good mixture of both worlds: I still have fine-grained control over hardware resources, and I get a decent api that is enjoyable to work with.

"But rewriting a full deep learning framework from scratch seems like a premature decision that will take too much time." I figured you might ask that. And maybe you'd be correct. But the project wasn't that big. Running `cloc . --exclude-content=kernels/ --exclude-lang=zig` on my `src/` folder gives me this:

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
HTML                             4             54              2            521
CSS                              2             48              0            403
Markdown                         2            122              0            343
Python                           1             56            191            127
-------------------------------------------------------------------------------
SUM:                             9            280            193           1394
-------------------------------------------------------------------------------
```

Most of the code lives in the `kernels/` folder with the `c` and `cuda` kernels. The project wasn't that large after all. So I decided to re-write the core in Zig, keep the kernels, and just use the `extern` keyword to link them in the build system. Same kernels, no re-write, but now the system is in a language I can actually enjoy working with. Win-win.

## The problem with hand-written kernels

The approach I'm using right now is hand-writing every single kernel for every operation. This is not ideal. First, it means too much code. In `c` that means writing optimized kernels for every data type. When writing `cuda` kernels, the execution configuration alone can make or break performance. And one of the most important optimization techniques in ML compilers — kernel fusion — becomes a nightmare of combinatorial explosion.

Kernel fusion is about writing a single kernel that composes multiple operations together. Take the most used `nn` layer in deep learning: `Linear`, which is basically `input @ weight.T + bias`. Why load `input` and `weights` from memory, do matmul, store the output, then load that result back to add `bias`, then store again? If you have been paying attention (congrats for not being brain-rotted) you'll notice we just did `(4) loads` and `(2) stores` across two separate function frames with jump operations in between. That shit is a performance killer.

With kernel fusion we write a single `matmul_add` kernel: matmul then add in the same frame. No jump ops. In this version we do `(3) loads` and `(1) store`. We saved one load and one store, which is significant because loads and stores are the most expensive operations in computer hardware.

With hand-written kernels we would need to write every fused variant separately, and all of them need to be exported to Zig. Plus the code is ugly. Look at this:

```cuda
__global__ void add_kernel_float_contig(const float *a, const float *b, float *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] + b[tid];
    }
}

__global__ void add_kernel_int_contig(const int *a, const int *b, int *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] + b[tid];
    }
}

__global__ void sub_kernel_float_contig(const float *a, const float *b, float *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] - b[tid];
    }
}

__global__ void sub_kernel_int_contig(const int *a, const int *b, int *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] - b[tid];
    }
}


__global__ void mul_kernel_float_contig(const float *a, const float *b, float *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] * b[tid];
    }
}

__global__ void mul_kernel_int_contig(const int *a, const int *b, int *c, int num_elements) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    if (tid < num_elements) {
        c[tid] = a[tid] * b[tid];
    }
}
```

And this is only for two data types, without even considering noncontiguous data layouts from slicing and movement ops like `broadcast` and `expand`.

## Codegen to the rescue

As a big fan of geohot, I was very interested in studying how tinygrad works. Tinygrad has a similar philosophy to `tvm`. Here's how `tvm` works: it captures the computation graph, lowers it to an `IR` representation, optimizes it with `MLIR`, and executes the optimized graph.

Tinygrad doesn't work exactly the same way, but the philosophy is similar. Instead of hand-writing every kernel — which is what I'm doing in plast — it has a `codegen` module. This module uses the `UOp` datatype to write kernels at runtime as needed. Using something called a `Linearizer`, it tries different optimization techniques like loop unrolling and shared memory usage on cuda, launches kernels with different configurations, and uses Beam Search to pick the fastest one.

You might think "this is very slow". You're not completely right, but you're not completely wrong either. It's slower on the first batch because it has to build the graph and write the optimized kernels. But with a JIT compiler we cache the resulting graph and kernels, so every subsequent batch uses them directly. This gives us a highly optimized graph without writing a kernel for every single combination of constraints.

Now let's look at how to generate all those ugly kernels from the previous section on the fly:

```zig
const std = @import("std");

pub const DataType = enum {
    float,
    int,

    pub fn toCudaTypeString(self: DataType) []const u8 {
        return switch (self) {
            .float => "float",
            .int => "int",
        };
    }
};

pub const OpType = enum {
    add,
    sub,
    mul,

    pub fn toChar(self: OpType) u8 {
        return switch (self) {
            .add => '+',
            .sub => '-',
            .mul => '*',
        };
    }
};

pub const Op = struct {
    op_type: OpType,
    data_type: DataType,

    pub fn generateKernel(self: Op, allocator: std.mem.Allocator) ![]const u8 {
        const op_name = @tagName(self.op_type);
        const type_name = @tagName(self.data_type);
        const type_c_str = self.data_type.toCudaTypeString();
        const op_char = self.op_type.toChar();

        const template =
            \\__global__ void {s}_kernel_{s}_contig(const {s} *a, const {s} *b, {s} *c, int num_elements) {{
            \\    int tid = blockDim.x * blockIdx.x + threadIdx.x;
            \\
            \\    if (tid < num_elements) {{
            \\        c[tid] = a[tid] {c} b[tid];
            \\    }}
            \\}}
            \\
        ;

        return try std.fmt.allocPrint(allocator, template, .{
            op_name,
            type_name,
            type_c_str,
            type_c_str,
            type_c_str,
            op_char,
        });
    }
};
```

With this we can generate kernels for any data type we want. With the right implementation, generating optimized kernels becomes elegant and maintainable instead of a copy-paste factory. That's why I think codegen is a much better approach than hand-written kernels.

## What's next for Plast

So where does this leave us? The plan is coming together: rewrite the core in Zig, keep the existing kernels, build a codegen module to replace the kernel copy-paste nightmare, wire it all into the JIT compiler, and finally — finally — have a framework I can actually use for reinforcement learning without wanting to throw my laptop out the window.

Right now I'm working on the Zig core and the codegen module in parallel. The kernels are already done and battle-tested from the C version, so that part is essentially free — just link and go. Once the codegen is mature enough to handle the full set of elementwise ops, I'll start fuzzing it against the hand-written kernels to make sure we don't regress on correctness or performance. After that, the hand-written versions go in the trash where they belong.

I don't know when the first version will be ready. Could be weeks, could be months. But for the first time this project actually feels fun again, and that's worth more than any release date.

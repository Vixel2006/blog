# What I Have Learnt Building My First SaaS Project

For the past few months, I've been building a SaaS project with some college mates. To be honest, I've always found the modern SaaS scene somewhat stupid. Most projects look like garbage to me—glorified AI wrappers attempting to solve problems that don't exist. Why would anyone need an "AI Alarm Clock"? Human beings are born with a free piece of technology called a biological clock. But hey, maybe the flagship humans are out of production, and the new economical models don't come with that feature built-in. Who am I to judge?

This is the story of how a failed hackathon project turned into a real-time API security platform called Argos, how we designed its architecture, and what I learnt along the way.

## 1. The Hackathon Genesis: An AI SIEM Mirage

The journey started five months ago at a college hackathon. A teammate opened his phone, prompted ChatGPT (or Gemini, I can't remember), and decided that our project would be a shiny "AI SIEM Solution." I'm not a cybersecurity maximalist; in fact, I've always found conventional security analytics incredibly boring. But as the lead for Machine Learning and Backend Engineering, I had to look into how SIEMs actually function under the hood.

I quickly realized we needed to pivot. Instead of post-incident log analysis (SIEM), we needed real-time protection at the application layer: an inline API security solution.

Because of extreme time constraints—and the fact that I hadn't slept for three days straight—I wrote some of the worst code of my life. The architecture was an absolute disaster:

```
+------------------+      Unstructured JSON      +----------------------+
| Inbound HTTP Req | --------------------------> |   Naive LLM Prompt   |
+------------------+                             +----------------------+
                                                            |
                                                            v
+------------------+       Massive Latency       +----------------------+
|  Blocked / Pass  | <-------------------------- |  "Retarded" SOC Bot  |
+------------------+                             +----------------------+
```

The pipeline ingested a raw JSON request, passed it wholesale to a massive LLM with a flimsy prompt, and asked it to investigate like a tier-one SOC analyst. No schema constraints, no input validation, no deterministic parsing. It was slow as hell, expensive as fuck, and completely impractical for real-world production traffic.

While waiting for the judges to inevitably smoke us during presentation day, the practical solution hit me. I thought about Stripe. They don't make you reroute your whole network; they provide lightweight, native SDKs that drop right into your backend code to handle the heavy lifting.

## 2. The Architecture Shift: Go Backend & Decoupled SDKs

We got cooked at the hackathon, but the technical challenge stuck with me. I thought it would be a fun experience.

I chose Go for the backend engine. I had never been a pure backend engineer—it doesn't give me the same rush as writing compilers or low-level systems infrastructure—but the team dynamics forced my hand. Out of a five-person team, only my close friend and I were actual builders. The other three were non-contributing partners who did nothing but talk. To make the platform a reality, we had to build fast.

Our core architectural blueprint decoupled the application runtime from the detection cluster using language-specific middlewares (SDKs):

```
   User Request
        |
        v
+---------------------------------------+
| Your Web App Runtime (Node/Python/Go) |
|                                       |
|  +---------------------------------+  |
|  |     Argos Middleware / SDK      |  |
|  +---------------------------------+  |
+---------------------------------------+
        |
        | Asynchronous / Synchronous Channel
        v
+---------------------------------------+
|       Argos Go Detection Engine       |
|                                       |
|  [Regex] -> [Statistical] -> [ML/DL]  |
+---------------------------------------+
```

To standardize behavioral tracking and model training, we normalized all incoming HTTP metadata into a strictly typed, unified exchange format. Here is a conceptual look at how our lightweight SDK middleware intercepts, extracts, and dispatches payload telemetry without blocking the hot-path:

```go
package argos

import (
	"bytes"
	"io"
	"net/http"
	"time"
)

type TelemetryPayload struct {
	Method    string            `json:"method"`
	Path      string            `json:"path"`
	Headers   map[string]string `json:"headers"`
	Body      string            `json:"body"`
	RemoteIP  string            `json:"remote_ip"`
	Timestamp int64             `json:"timestamp"`
}

func ArgosMiddleware(client *ArgosClusterClient) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			var bodyBytes []byte
			if r.Body != nil {
				bodyBytes, _ = io.ReadAll(r.Body)
				r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
			}

			payload := TelemetryPayload{
				Method:    r.Method,
				Path:      r.URL.Path,
				Headers:   extractHeaders(r.Header),
				Body:      string(bodyBytes),
				RemoteIP:  r.RemoteAddr,
				Timestamp: time.Now().UnixNano(),
			}

			go client.Analyze(payload)

			next.ServeHTTP(w, r)
		})
	}
}
```

## 3. Optimizing the Pipeline: Mechanical Pentesting

During my university final exams, I needed a productive way to procrastinate. Instead of studying legacy rendering hooks for my Computer Graphics course, I started learning web application penetration testing.

I realized something critical: Web pentesting is deeply mechanical. When an attacker or an automated scanner maps an API, they systematically spray known, highly predictable structural patterns against your endpoints to check for vulnerabilities (SQLi, XSS, Path Traversal).

If we can catch those mechanical trials on the ultra-fast hot path using a strict cascade of deterministic filters, we don't need a heavy deep learning model or a slow LLM for standard exploitation attempts.

### The Multi-Tier Inspection Stack

We abandoned the single, slow LLM bottleneck and built a multi-tier pipeline:

1. **Deterministic Filter (Regex & Tokenizer)**: Instantly drops obvious, raw signatures (e.g., `' OR 1=1 --`, `<script>`).

2. **Statistical Analyzer**: Evaluates entropy variations, character distribution shifts, and structural anomalies in the payload lengths.

3. **Machine Learning / Deep Learning Module**: Processes deep contextual threats only when the first two layers raise suspicion flags.

```
Incoming Payload
      |
      v
  +----------------------------------+
  | Tier 1: Deterministic Regex/Tok  | ---> [Signature Match] -> Immediate IP Block
  +----------------------------------+
      | Clean
      v
  +----------------------------------+
  | Tier 2: Statistical Entropy      | ---> [Anomalous Deviation] -> Trigger ML/DL
  +----------------------------------+
      | Clean
      v
  +----------------------------------+
  | Tier 3: Contextual ML/DL Models  | ---> [Malicious Intent] -> Action & Flag
  +----------------------------------+
```

By instantly dropping an automated firewall block on the attacker's IP the moment a mechanical signature is hit, we break the attacker's feedback loop. If a malicious actor has to rotate their proxy or IP address after every single exploit variation, the cost of attack skyrockets, and they move on.

## 4. What I Have Learnt

**Engineering Isn't Everything**: As a developer, I love pure infrastructure engineering, but business is driven by distribution. A bulletproof software engine is useless if you cannot market it or convince customers of its monetization value, which is why I hate business.

**Backend Development is Manageable**: It lacks the elegance of compiler design or low-level ML hardware execution layers, but building highly concurrent systems in Go to process massive request streams is a solid engineering challenge.

**People Come and Go**: Protect your peace, build exclusively with active creators, and don't optimize for making passengers comfortable. As Drake cleanly put it in *Fair Trade*:

> "I've been losing friends and finding peace, honestly that sounds like a fair trade to me."

## The Roadmap

The platform is live at [argossecops.com](https://argossecops.com). Our long-term strategy is an open-core model, keeping our core high-concurrency detection engine proprietary while open-sourcing our client SDK libraries and middlewares. We are currently moving cautiously with the open-source rollout to safeguard our early proprietary logic, while focusing heavily on expanding our active user base and distribution.

The stack is fast, the engine is clean, and we're just getting started. If you're a developer looking to lock down your APIs without slaughtering your request-response latency, check us out.

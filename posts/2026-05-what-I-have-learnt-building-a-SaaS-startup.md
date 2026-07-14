# What I Learnt Building a SaaS (And Why the Startup Scene is Cancer)

For the past few months, I've been building a SaaS project with some college mates. To be completely honest, I've always found the modern SaaS scene incredibly stupid. Most projects look like absolute garbage to me—glorified AI wrappers attempting to solve problems that don't exist. Why would anyone need an "AI Alarm Clock"? Human beings are born with a free piece of technology called a biological clock. But hey, maybe the flagship humans are out of production, and the new economical models don't come with that feature built-in. Who am I to judge?

Actually, I will judge. The entire startup ecosystem is a disease. It's a playground where marketing, hype, and VC-pleasing buzzwords weigh infinitely more than the actual value or engineering quality of the solution. It's the natural result of late-stage capitalism: a system that doesn't care about creating things that are useful or elegant, but instead incentivizes grifters to build bloated, useless tools just to extract subscription fees. 

This is the story of how we took a failed, hype-driven hackathon project, stripped away the AI bullshit, and built a real-time API security platform called Argos—along with what I learnt about code, useless people, and why the tech industry is broken.

---

## 1. The Hackathon Genesis: An AI SIEM Mirage

The journey started five months ago at a college hackathon. A teammate opened his phone, prompted ChatGPT (or Gemini, I can't remember), and immediately declared that our project would be a shiny "AI SIEM Solution." I've always found conventional security analytics incredibly boring, but as the lead for Machine Learning and Backend Engineering, I had to look into how SIEMs actually function under the hood.

I quickly realized we needed to pivot. Instead of post-incident log analysis (SIEM)—which is just looking at the ashes of your server after it already burned down—we needed real-time protection at the application layer. An inline API security solution.

Because of extreme time constraints—and the fact that I hadn't slept for three days straight—I wrote some of the worst code of my life. The initial architecture was an absolute disaster:

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

The pipeline took a raw JSON request, passed it wholesale to a massive LLM with a flimsy prompt, and asked it to act like a tier-one SOC analyst. No schema constraints, no input validation, and zero deterministic parsing. It was slow as hell, expensive as fuck, and completely impractical for real-world production traffic. It was the perfect representation of modern "AI engineering"—retarded, bloated, and useless.

While waiting for the judges to inevitably smoke us during presentation day, the practical solution hit me. I thought about Stripe. They don't make you reroute your whole network through a slow proxy; they provide lightweight, native SDKs that drop right into your backend code to handle the heavy lifting.

---

## 2. The Architecture Shift: Go Backend & Decoupled SDKs

We got cooked at the hackathon, but the technical challenge stuck with me. Even though the business side of SaaS makes me sick, I thought building the actual engine would be a fun engineering exercise.

I chose Go for the backend engine. I've never been a pure backend engineer—building CRUD APIs doesn't give me the same rush as writing compilers, operating systems, or low-level systems infrastructure—but the team dynamics forced my hand. Out of a five-person team, only my close friend and I were actual builders. The other three were non-contributing passengers who did absolutely nothing but talk, show up to meetings, and repeat corporate jargon they probably read on LinkedIn. 

To make the platform a reality without losing my mind, we had to build fast and bypass the dead weight.

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
	"net/netip"
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

			// Run in a goroutine to avoid blocking the main request thread
			go client.Analyze(payload)

			next.ServeHTTP(w, r)
		})
	}
}
```

---

## 3. Optimizing the Pipeline: Mechanical Pentesting

During my university final exams, I needed a productive way to procrastinate. Instead of studying legacy rendering hooks for my Computer Graphics course, I started learning web application penetration testing.

I quickly realized something critical: Web pentesting is deeply mechanical. When an attacker or an automated scanner maps an API, they systematically spray known, highly predictable structural patterns against your endpoints to check for vulnerabilities (SQLi, XSS, Path Traversal).

If you can catch those mechanical trials on the ultra-fast hot path using a strict cascade of deterministic filters, you don't need a heavy deep learning model or a slow LLM for standard exploitation attempts.

### The Multi-Tier Inspection Stack

We threw the single, slow LLM bottleneck in the trash and built a multi-tier pipeline:

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

---

## 4. What I Learnt (The Hard Way)

**Capitalism is the Cancer of Software**: 
As a developer, I love pure engineering, solving complex algorithmic bottlenecks, and writing clean, minimal code. But in our capitalistic society, none of that matters. Capitalism does not reward good engineering; it rewards marketing grift. A bulletproof software engine is useless in the market if you cannot write slick copy, buy ads, and convince corporate managers to buy it. This is why I absolutely despise the startup scene. It forces talented builders to stop building and start selling, converting engineering passion into corporate marketing noise.

**Most People Just Want a Free Ride**: 
You will quickly learn that most people suck. In group projects, hackathons, and startups, you will always find passengers—people who want the title, the equity, and the glory, but won't write a single line of code. They will spend hours talking about "strategy" and "positioning" to cover up the fact that they have zero technical skills. Build exclusively with active creators, protect your peace, and kick the dead weight out early. As Drake put it in *Fair Trade*:

> "I've been losing friends and finding peace, honestly that sounds like a fair trade to me."

**Backend is Fine, but It's Not Compilers**:
Go is a highly concurrent, practical language for processing request streams, but backend development still lacks the intellectual beauty of compiler design or low-level systems. At the end of the day, building a SaaS often feels like assembling pre-existing puzzle pieces. But if you have to do it, at least do it without the typical corporate bloat.

---

## The Reality of the Roadmap

The platform is live at [argossecops.com](https://argossecops.com). We are using an open-core model, keeping our core high-concurrency detection engine proprietary while open-sourcing our client SDKs. 

Is it a revolutionary breakthrough in computer science? No. At its core, it's just a fast, clean, multi-tiered firewall and detection system. But unlike the bloated, VC-backed "AI security" garbage polluting the internet today, it actually works, it doesn't kill your request latency, and it doesn't feed your sensitive data to OpenAI. 

If you're a developer who cares about performance and wants to secure your APIs without adopting 200MB of dependencies and a slow AI proxy, check it out. Or don't. At least the code is clean.

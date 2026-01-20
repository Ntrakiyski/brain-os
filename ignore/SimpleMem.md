SimpleMem: Efficient Lifelong Memory for LLM Agents
Jiaqi Liu 1 * Yaofeng Su 1 * Peng Xia 1 Siwei Han 1
Zeyu Zheng 2 Cihang Xie 3 Mingyu Ding 1 Huaxiu Yao 1
Abstract
To support reliable long-term interaction in com-plex environments, LLM agents require mem-ory systems that efficiently manage historical experiences. Existing approaches either retain full interaction histories via passive context ex-tension, leading to substantial redundancy, or rely on iterative reasoning to filter noise, in-curring high token costs. To address this chal-lenge, we introduce SimpleMem, an efficient memory framework based on semantic lossless compression. We propose a three-stage pipeline designed to maximize information density and token utilization: (1) Semantic Structured Com-pression, which applies entropy-aware filtering to distill unstructured interactions into compact, multi-view indexed memory units; (2) Recur-sive Memory Consolidation, an asynchronous process that integrates related units into higher-level abstract representations to reduce redun-dancy; and (3) Adaptive Query-Aware Retrieval, which dynamically adjusts retrieval scope based on query complexity to construct precise context efficiently. Experiments on benchmark datasets show that our method consistently outperforms baseline approaches in accuracy, retrieval effi-ciency, and inference cost, achieving an aver-age F1 improvement of 26.4% while reducing inference-time token consumption by up to 30×, demonstrating a superior balance between per-formance and efficiency. Code is available at https://github.com/aiming-lab/SimpleMem.
1. Introduction Large Language Model (LLM) agents have recently demon-strated remarkable capabilities across a wide range of
*Equal contribution 1UNC-Chapel Hill 2University of Cal-ifornia, Berkeley 3University of California, Santa Cruz. Cor-respondence to: Jiaqi Liu <jqliu@cs.unc.edu>, Mingyu Ding <md@cs.unc.edu>, Huaxiu Yao <huaxiu@cs.unc.edu>.
Preprint. January 7, 2026.
tasks (Xia et al., 2025; Team et al., 2025; Qiu et al., 2025). However, constrained by fixed context windows, existing agents exhibit significant limitations when engaging in long-context and multi-turn interaction scenarios (Liu et al., 2023; Wang et al., 2024a; Liu et al., 2025; Hu et al., 2025; Tu et al., 2025). To facilitate reliable long-term interaction, LLM agents require robust memory systems to efficiently manage and utilize historical experience (Dev & Taranjeet, 2024; Fang et al., 2025; Wang & Chen, 2025; Tang et al., 2025; Yang et al., 2025; Ouyang et al., 2025).
While recent research has extensively explored the design of memory modules for LLM agents, current systems still suffer from suboptimal retrieval efficiency and low token utilization (Fang et al., 2025; Hu et al., 2025). On one hand, many existing systems maintain complete interaction histo-ries through full-context extension (Li et al., 2025; Zhong et al., 2024). However, this approach introduce substantial redundant information (Hu et al., 2025). Specifically, during long-horizon interactions, user inputs and model responses accumulate substantial low-entropy noise (e.g., repetitive logs, non-task-oriented dialogue), which degrades the effec-tive information density of the memory buffer. This redun-dancy adversely affects memory retrieval and downstream reasoning, often leading to middle-context degradation phe-nomena (Liu et al., 2023), while also incurring significant computational overhead during retrieval and secondary infer-ence. On the other hand, some agentic frameworks mitigate noise through online filtering based on iterative reasoning procedures (Yan et al., 2025; Packer et al., 2023). Although such approaches improve retrieval relevance, they rely on repeated inference cycles, resulting in substantial compu-tational cost, including increased latency and token usage. As a result, neither paradigm achieves efficient allocation of memory and computation resources.
To address these limitations, we introduce SimpleMem, an efficient memory framework inspired by the Complemen-tary Learning Systems (CLS) theory (Kumaran et al., 2016) and designed around structured semantic compression. The core objective of SimpleMem is to improve information efficiency under fixed context and token budgets. To this end, we develop a three-stage pipeline that supports dy-namic memory compression, organization, and adaptive retrieval: (1) Semantic Structured Compression: we ap-
1
https://lh3.googleusercontent.com/notebooklm/AG60hOr7o3OcX8sVEZkgvfjVz1tGTHbkJzrU3VPBObCp-OjD0PqVlrG2LD5dfwOkRGn_18vlxncOyr_LzmpHN424M0lm4I3mw5K58m9kldq8h3pxE1T6xlv7dy9Gat7W9aQA9zE9WHH0xw=w152-h146-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOr7YVyluYBiS8rScaOBRwdBa7Fvr8MXeknI9-2hCGK5fb2QF9W8Mrpy2tqRIMt2nC4XWfcfB9zvQ5F3oD9iJs2aJZtqAotEwuWgRdO78-VjKb583vdGFzrxNBC6bnmtiOzjpfXj=w433-h124-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOoyBqdhIIVEUBJAjJqwyPsaJKFfNGxamFLZ3KlWJkMB8WvD9STGIChAEqHWBZTxTF_PJ1I7y0TudVXbWHWX7k5225fYmof2QAy8__Zh1KShWluhUtlC1jlVrzBjCFQ7aKzY8W5WQA=w1157-h659-v0
SimpleMem: Efficient Lifelong Memory for LLM Agents
LoCoMo(Full)
ReadAgent
MemoryBank
MemGPT
A-Mem
LightMem
Mem0
SimpleMem (Ours)
Average Token Cost (Log Scale)
Pe rf
or m
an ce
(F 1
Sc or
e)
10!10"
10
20
30
40
50 SimpleMem (Ours)
Figure 1. Performance vs. Efficiency Trade-off. Comparison of Average F1 against Average Token Cost on the LoCoMo bench-mark. SimpleMem occupies the ideal top-left position, achieving high accurac with minimal token consumption (∼550 tokens).
ply an entropy-aware filtering mechanism that preserves information with high semantic utility while discarding re-dundant or low-value content. The retained information is reformulated into compact memory units and jointly indexed using dense semantic embeddings, sparse lexical features, and symbolic metadata, enabling multi-granular retrieval. (2) Recursive Memory Consolidation: Inspired by biolog-ical consolidation, we introduce an asynchronous process that incrementally reorganizes stored memory. Rather than accumulating episodic records verbatim, related memory units are recursively integrated into higher-level abstract representations, allowing repetitive or structurally similar experiences to be summarized while reducing semantic redundancy. (3) Adaptive Query-Aware Retrieval: we employ a query-aware retrieval strategy that dynamically adjusts retrieval scope based on estimated query complex-ity. Irrelevant candidates are pruned through lightweight symbolic and semantic constraints, enabling precise context construction tailored to task requirements. This adaptive mechanism achieves a favorable trade-off between reason-ing performance and token efficiency.
Our primary contribution is SimpleMem, an efficient mem-ory framework grounded in structured semantic compres-sion, which improves information efficiency through prin-cipled memory organization, consolidation, and adaptive retrieval. As shown in Figure 1, our empirical experiments demonstrate that SimpleMem establishes a new state-of-the-art with an F1 score, outperforming strong baselines like Mem0 by 26.4%, while reducing inference token consump-tion by 30× compared to full-context models.
2. The SimpleMem Architecture In this section, we present SimpleMem, an efficient mem-ory framework for LLM agents designed to improve in-formation utilization under constrained context and token budgets through. As shown in Figure 2, the system op-erates through a three-stage pipeline. First, we describe Semantic Structured Compression process, which filters re-dundant interaction content and reformulates raw dialogue
streams into compact memory units. Next, we describe Re-cursive Consolidation, an asynchronous process that incre-mentally integrates related memory units into higher-level abstract representations and maintaining a compact memory topology. Finally, we present Adaptive Query-Aware Re-trieval, which dynamically adjusts retrieval scope based on estimated query complexity to construct precise and token-efficient contexts for downstream reasoning.
2.1. Semantic Structured Compression
A primary bottleneck in long-term interaction is context inflation, the accumulation of raw, low-entropy dialogue. For example, a large portion of interaction segments in the real-world consists of phatic chit-chat or redundant confir-mations, which contribute little to downstream reasoning but consume substantial context capacity. To address this, we introduce a mechanism to actively filter and restructure information at the source.
First, incoming dialogue is segmented into overlapping slid-ing windows Wtof fixed length, where each window repre-sents a short contiguous span of recent interaction. These windows serve as the basic units for evaluating whether new information should be stored. Then we employ a non-linear gating mechanism, Φgate,to evaluate the information den-sity of these dialogue windows to determine which windows is used fo indexing. For each window Wt,we compute an information score H(WT) that jointly captures the intro-duction of new entities and semantic novelty relative to the immediate interaction history Hprev.
Formally, let Enewdenote the set of named entities that appear in Wtbut not in Hprev.The information score is defined as:
H(Wt)= α⋅∣Enew∣∣Wt∣
+(1−α)⋅(1−cos(E(Wt),E(Hprev)))
(1) where E(⋅)denotes a semantic embedding function and αcontrols the relative importance of entity-level novelty and semantic divergence.
Windows whose information score falls below threshold τredundantare treated as redundant and excluded from memory construction, meaning that the window is neither stored nor further processed, preventing low-utility interaction content from entering the memory buffer. For informative windows, the system proceeds to a segmentation step:
Action(Wt)=
{ Segment(Wt),H(Wt)≥τredundant,
∅,otherwise.(2)
For windows that pass the filter, we apply a segmentation function Fθto decompose each informative window into a set of context-independent memory units mk.This trans-
2
https://lh3.googleusercontent.com/notebooklm/AG60hOrMVKnxWRdm4H-G7M3HWzgwYj5rDl-6a5RFcuSw-Svqm4144Ew6ue77XVYOvLa85LpHzyEHwgZLKO6T8plMxFW1xR2CwJty0zk__v43a0MIni80sXTajvdjayGEe2grQGWT04F4ug=w62-h55-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrbm_rgvoSoQIaAmnoXwwVwBrXASjguXL_18u9hfxjZZaKGr355KrLkxzx-G46YGEPrhwJ8yUn7RD1CCRS0_n1qoTW6fYLg4v6Zgfa3h0HcErcJP52-6GG-tUpPx7v7l47BmGZqGA=w65-h55-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrn-tISO4vJG3p7WcwX5-Gp26L2XC09fonmPEZT7cNsEXiz0b7nb1ujT7jFw-qeF7p_Jf0FZj67ghuEtpUwTYknRP29yVmzwOXro25psyEiAIMwj7OFfRJ2p0KQh4n8csfDKiGaFA=w41-h55-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrU01kBCWX-FUoB_C6queZd9XaxWgZj_jxQNYSgCR40uwmgsSExWk18HsiUcAbqaTZj6my7WOnBemArax_aEYbHrjPKC_rMA1rwq2Pow0-HUsrYzqtZpikc6jiFGTH5SV2pMpZG=w41-h55-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOqHAOO68-7kdyFlhQFaOTtOTlIXL4yAwUUvyhIiLctR0oM_ZE7P46l1WTUPKSrM3Z5vI4YAhvymiHVxPo6T1y2hDTr4OMLl52MWLJ2lALgAPL21G8spjbvliKEpunwGaggQC-ot=w69-h55-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrymKgXXy_xhZBs6m0Ino_8kX9fftHMWFo01mTxO55SePuNTnkZKGGB6_cgIHWDRO4u8NYY0UBpJJzP89F_pC7L8rKleNDPlD70xBw0P_kW_6u4XkHJ6G1J8bPIU0GZwMk_dMSRdQ=w65-h34-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOqcfWt1oCZrzGOUsmoanLRhA4h4uNZyCwnnn4Yt6oQpXtdl1adCMYLlaGwESY76y3yv2GDoKAQYR5ii8OtA9u3wiWOBO20UJVmN1T7qo8iSM61G24YiDRkbGQ623oNU1xVOwmwxDA=w900-h940-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOqmEpgz69rp6z7DjhArb5ugq5fkSCiTQwwGfjnzNN1oXgQLatPdrRUIuLXKJReWlHD1xRb25nhPVkubH-DS3RmKMiNSPlrjgza--U6uL88rSbj341kj2rSHMkM1bVi-vhUTb1eqAw=w128-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOp26f74ei1vyf1uPMOIVXmVHY8-tQg_NGvY4byWA6gXVGMM11m-c6PZsnemgCcCGFQgBOhu94OKgCiIRXoNfbXUdu78-PJJkBK-sDGFlyu0DBKzafb1nFKHugCGB7rDKQgdo5ll_g=w128-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOooeU6Zt19lF8tAffJj47f6AwNGEwPfvQjKACkjEfGbuwHInFrJGodLt1TSy40rFKN0EaSi4lNQRn2fiHaGVGs-K8cLnr7OuY4jDGr1IqLkP0stHwj8ZK-wcYlEBcwc7hhtYgILYA=w128-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrAvLQja9c9_cQgqfVMlFVmXPWuJM1QEE5pB1iiwpK-1A3udMHIYW__1d4ttKfHWt9L8heRMoVJlhZ1ihuKYEC70id5vjRgNAixA_tieU-xPn6r-QztVGLNpkRbkx1n8nxrvwNtLw=w128-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOp2W4QfSRD6aT9qnx6oSOBNFMBrJJhagteHVoU5NWqj1dbVTEVizursvc51Q1UFNynPC0vgLLC8_UPTST3qDmIjYI47_kuzSukeLBBE7nkJMUoVOQ199Uqs6tvXvw2aDeDDTEpI3w=w128-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOpQ3gqURHIwlqnFmxopsTAdvOZAmnlXnHQpOlNarDVEIAWpDRttlFAzW-AVcj4EQ_j7oSZlU_dLe4i1z7unTV0A-g_aXHta4STtsEacxoOrqHHVWqXhnwzueoQRRRzy7LucubQ4Kw=w59-h59-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOpVU7vJScGot-H1LTya5wiufSQv0lmo5JM7NlJZJC9uznTJ5BzSshLDSaBau19ZCcrB9okUC5Sym7uJQBlFQBiag76TaW7C-BZG37Mo9pBD2bW5XhQZnv83RoxoUvjnPcMPyCsb_A=w48-h47-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOojFpCAyGghRUZPsSKClAa0LkEVzcOylqqzA07ULreFXaFqNk0MT1OwsTCBMz0YvbuOhoGhX-DF3h6eVCLEUAEp1set5aH-8PbU7mOBE49Z7AUbXCLq8rbYfJueWFPK7luJPBqDXw=w47-h47-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOrXBsIzWeQsgeobkEIj12WyVbWePbzVtLZydDHIBthSsVhOSWM-Hk7ItvSS_VLJqsHgh5je9ZYdD5ULaV6p46UIftcLGJZTks5-n44OYrSagVyRfFti0UJ4MsnTOiiXnuadx9Rzyg=w122-h138-v0
SimpleMem: Efficient Lifelong Memory for LLM Agents
Semantic Structured Compression
Noise
Information
Entropy Filter
Memory Units
Recursive Consolidation
Lexical Layer
Semantic Layer
Symbolic Layer
Structured Indexing
Hyper-Node Atom 1
Affinity $score 𝑤!,# $
Atom 2
Dense Cluster
User Query
Complexity Estimator
Adaptive Pruning
Context Synthesis
Output
Adaptive Retrieval
Figure 2. The SimpleMem Architecture. SimpleMem mitigates context inflation through three stages. (1) Semantic Structured Compression filters redundant interaction content and reformulates raw dialogue into compact, context-independent memory units. (2) Recursive Consolidation incrementally organizes related memory units into higher-level abstract representations, reducing redundancy in long-term memory. (3) Adaptive Query-Aware Retrieval dynamically adjusts retrieval scope based on query complexity, enabling efficient context construction under constrained token budgets.
formation resolves dependencies implicit in conversational flow by converting entangled dialogue into self-contained factual or event-level statements. Formally, Fθis composed of a coreference resolution module (Φcoref)and a temporal anchoring module (Φtime):
mk= Fθ(Wt)= Φtime
• Φcoref
• Φextract(Wt)(3)
Here, Φextractidentifies candidate factual statements, (Φcoref) replaces ambiguous pronouns with specific entity names (e.g., changing "He agreed" to "Bob agreed"), and Φtimeconverts relative temporal expressions (e.g., transform-ing "next Friday" to "2025-10-24") into absolute ISO-8601 timestamps. This normalization ensures that each mem-ory unit remains interpretable and valid independent of its original conversational context.
2.2. Structured Indexing and Recursive Consolidation
Then, the system need organize the resulting memory units to support efficient long-term storage and scalable retrieval. This stage consists of two components: (i) structured multi-view indexing for immediate access, and (ii) recursive con-solidation for reducing redundancy and maintaining a com-pact memory topology over time.
To support flexible and precise retrieval, each memory unit is indexed through three complementary representations. First, at sematic layer, we map the entry to a dense vector space vkusing embedding models, which captures abstract meaning and enables fuzzy matching (e.g., retrieving "latte" when querying "hot drink"). Second, the Lexical Layer generates a sparse representation focusing on exact keyword matches and proper nouns, ensuring that specific entities are not diluted in vector space. Third, the Symbolic Layer extracts structured metadata, such as timestamps and entity types, to enable deterministic filtering logic. Formally, these
projections form the comprehensive memory bank M:
M(mk)=
 vk= Edense(Sk)∈Rd(Semantic Layer) hk= Sparse(Sk)∈R∣V| (Lexical Layer) Rk= ${(key, $val)} (Symbolic Layer)
(4) It allows the system to flexibly query information based on conceptual similarity, exact keyword matches, or structured metadata constraints.
While multi-view indexing supports efficient access, naively accumulating memory units over long interaction horizons leads to redundancy and fragmentation. To address this is-sue, we then introduces an asynchronous background consol-idation process that incrementally reorganizes the memory topology. The consolidation mechanism identifies related memory units based on both semantic similarity and tempo-ral proximity. For two memory units miand mj, we define an affinity score ωijas:
ωij= β· cos(vi,vj)+ (1− β)· e−λ∣ti−tj∣,(5)
where the first term captures semantic relatedness and the second term biases the model toward grouping events with strong temporal proximity.
When a group of memory units forms a dense cluster C, de-termined by pairwise affinities exceeding a threshold τcluster,the system performs a consolidation step:
Mabs= $Gsyn({mi $| $mi ∈ C}). $(6)
This operation synthesizes repetitive or closely related memory units into a higher-level abstract representation Mabs,which captures their shared semantic structure. For example, instead of maintaining numerous individ-ual records such as “the user ordered a latte at 8:00 AM,” the system consolidates them into a single abstract pattern, e.g., “the user regularly drinks coffee in the morning.” The original fine-grained entries are archived, reducing the active mem-ory size while preserving the ability to recover detailed
3
SimpleMem: Efficient Lifelong Memory for LLM Agents
information if needed. As a result, the active memory index remains compact, and retrieval complexity scales gracefully with long-term interaction history.
2.3. Adaptive Query-Aware Retrieval
After memory entries are organized, another challenge to retrieve relevant information efficiently under constrained context budgets. Standard retrieval approaches typically fetch a fixed number of context entries, which often results in either insufficient information or token wastage. To ad-dress this, we introduces an adaptive query-aware retrieval mechanism that dynamically adjusts retrieval scope based on estimated query complexity, thereby improving retrieval efficiency without sacrificing reasoning accuracy.
First, we propose a hybrid scoring function for information retrieval, S(q,mk),which aggregates signals from the tri-layer index established in the second stage. For a given query q,the relevance score is computed as:
S(q,mk)= λ1cos(eq,vk)+ λ2BM25(qlex,Sk)
+ γI(Rk|= Cmeta),(7)
where the first term measures semantic similarity in the dense embedding space, the second term captures exact lexical relevance, and the indicator function I(·) enforces hard symbolic constraints such as entity-based filters.
Then, based on the hybrid scoring, we can rank the candi-date memories by relevance. However, retrieving a fixed number of top-ranked entries remains inefficient when query demands vary. To address this, we estimate the query com-plexity Cq∈[0,1], which reflects whether a query can be resolved via direct fact lookup or requires multi-step reason-ing over multiple memory entries. A lightweight classifier predicts Cqbased on query features such as length, syntactic structure, and abstraction level.
kdyn= ⌊kbase· (1 + δ· Cq)⌋(8)
Based on this dynamic depth, the system modulates the retrieval scope. For low-complexity queries (Cq→0), the system retrieves only the top−kminhigh-level abstract memory entries or metadata summaries, minimizing token usage. Conversely, for high-complexity queries (Cq→1), it expands the scope to top−kmax,including a larger set of relevant entries, along with associated fine-grained details. The final context Cfinalis synthesized by concatenating these pruned results, ensuring high accuracy with minimal computational waste:
Cfinal= ⊕
m∈Top−kdyn(S)
[tm: Content(m)](9)
3. Experiments In this section, we evaluate SimpleMem on the benchmark to answer the following research questions: (1) Does Simple-Mem outperform other memory systems in complex long-term reasoning and temporal grounding tasks? (2) Can SimpleMem achieve a superior trade-off between retrieval accuracy and token consumption? (3) How effective are the proposed components? (4) What factors account for the observed performance and efficiency gains?
3.1. Experimental Setup
Benchmark Dataset. We utilize the LoCoMo benchmark (Maharana et al., 2024), which is specifically designed to test the limits of LLMs in processing long-term conversa-tional dependencies. The dataset comprises conversation samples ranging from 200 to 400 turns, containing complex temporal shifts and interleaved topics. The evaluation set consists of 1,986 questions categorized into four distinct reasoning types: (1) Multi-Hop Reasoning: Questions re-quiring the synthesis of information from multiple disjoint turns (e.g., “Based on what X said last week and Y said today...”); (2) Temporal Reasoning: Questions testing the model’s ability to understand event se-quencing and absolute timelines (e.g., “Did X happen before Y?”); (3) Open Domain: General knowledge questions grounded in the conversation context; (4) Sin-gle Hop: Direct retrieval tasks requiring exact matching of specific facts.
Baselines. We compare SimpleMem with representa-tive memory-augmented systems: LOCOMO (Maharana et al., 2024), READAGENT (Lee et al., 2024), MEMORY-BANK (Zhong et al., 2024), MEMGPT (Packer et al., 2023), A-MEM (Xu et al., 2025), LIGHTMEM (Fang et al., 2025), and Mem0 (Dev & Taranjeet, 2024).
Backbone Models. To test robustness across capability scales, we instantiate each baseline and SimpleMem on multiple LLM backends: GPT-4o, GPT-4.1-mini, Qwen-Plus, Qwen2.5 (1.5B/3B), and Qwen3 (1.7B/8B).
Implementation Details. For semantic structured compres-sion, we use a sliding window of size W= 10 and set the entropy-based significance threshold to τ= 0.35to filter low-information interaction content. Memory index-ing is implemented using LanceDB with a multi-view de-sign: text-embedding-3-small (1536 dimensions) for dense semantic embeddings, BM25 for sparse lexical indexing, and SQL-based metadata storage for symbolic attributes. Recursive consolidation is triggered when the average pairwise semantic similarity within a memory clus-ter exceeds τcluster= 0.85.During retrieval, we employ adaptive query-aware retrieval, where the retrieval depth is dynamically adjusted based on estimated query complexity,
4
SimpleMem: Efficient Lifelong Memory for LLM Agents
Table 1. Performance on the LoCoMo benchmark with High-Capability Models (GPT-4.1 series and Qwen3-Plus). SimpleMem achieves superior efficiency-performance balance.
Model Method MultiHop Temporal OpenDomain SingleHop Average Token F1 BLEU F1 BLEU F1 BLEU F1 BLEU F1 BLEU Cost
GPT-4.1-mini
LoCoMo 25.02 21.62 12.04 10.63 19.05 17.07 18.68 15.87 18.70 16.30 16,910 ReadAgent 6.48 5.6 5.31 4.23 7.66 6.62 9.18 7.91 7.16 6.09 643 MemoryBank 5.00 4.68 5.94 4.78 5.16 4.52 5.72 4.86 5.46 4.71 432 MemGPT 17.72 16.02 19.44 16.54 11.29 10.18 25.59 24.25 18.51 16.75 16,977 A-Mem 25.06 17.32 51.01 44.75 13.22 14.75 41.02 36.99 32.58 28.45 2,520 LightMem 24.96 21.66 20.55 18.39 19.21 17.68 33.79 29.66 24.63 21.85 612 Mem0 30.14 27.62 48.91 44.82 16.43 14.94 41.3 36.17 34.20 30.89 973 SimpleMem 43.46 38.82 58.62 50.10 19.76 18.04 51.12 43.53 43.24 37.62 531
GPT-4o
LoCoMo 28.00 18.47 9.09 5.78 16.47 14.80 61.56 54.19 28.78 23.31 16,910 ReadAgent 14.61 9.95 4.16 3.19 8.84 8.37 12.46 10.29 10.02 7.95 805 MemoryBank 6.49 4.69 2.47 2.43 6.43 5.30 8.28 7.10 5.92 4.88 569 MemGPT 30.36 22.83 17.29 13.18 12.24 11.87 40.16 36.35 25.01 21.06 16,987 A-Mem 32.86 23.76 39.41 31.23 17.10 15.84 44.43 38.97 33.45 27.45 1,216 LightMem 28.15 21.83 36.53 29.12 13.38 11.54 33.76 28.02 27.96 22.63 645 Mem0 35.13 27.56 52.38 44.15 17.73 15.92 39.12 35.43 36.09 30.77 985 SimpleMem 35.89 32.83 56.71 20.57 18.23 16.34 45.41 39.25 39.06 27.25 550
Qwen3-Plus
LoCoMo 24.15 18.94 16.57 13.28 11.81 10.58 38.58 28.16 22.78 17.74 16,910 ReadAgent 9.52 6.83 11.22 8.15 5.41 5.23 9.85 7.96 9.00 7.04 742 MemoryBank 5.25 4.94 1.77 6.26 5.88 6.00 6.90 5.57 4.95 5.69 302 MemGPT 25.80 17.50 24.10 18.50 9.50 7.80 40.20 42.10 24.90 21.48 16,958 A-Mem 26.50 19.80 46.10 35.10 11.90 11.50 43.80 36.50 32.08 25.73 1,427 LightMem 28.95 24.13 42.58 38.52 16.54 13.23 40.78 36.52 32.21 28.10 606 Mem0 32.42 21.24 47.53 39.82 17.18 14.53 46.25 37.52 35.85 28.28 1,020 SimpleMem 33.74 29.04 50.87 43.31 18.41 16.24 46.94 38.16 37.49 31.69 583
ranging from kmin= 3 for simple lookups to kmax= 20 for complex reasoning queries.
Evaluation Metrics. We report: F1 and BLEU-1 (ac-curacy), Adversarial Success Rate (robustness to dis-tractors), and Token Cost (retrieval/latency efficiency). LongMemEval-S uses its standard accuracy-style metric.
3.2. Main Results and Analysis
We evaluate SimpleMem across a diverse set of LLMs, rang-ing from high-capability proprietary models (GPT-4o series) to efficient open-source models (Qwen series). Tables 1 and 2 present the detailed performance comparison on the LoCoMo benchmark.
Performance on High-Capability Models. As shown in Ta-ble 1, SimpleMem consistently outperforms existing mem-ory systems across all evaluated models. On GPT-4.1-mini, SimpleMem achieves an Average F1 of 43.24, establish-ing a significant margin over the strongest baseline, Mem0 (34.20), and surpassing the full-context baseline (LoCoMo, 18.70) by over 24 points. Notable gains are observed in Temporal Reasoning, where SimpleMem scores 58.62 F1 compared to Mem0’s 48.91, demonstrating the effective-ness of our Semantic Structured Compression in resolving complex timelines. Similarly, on the flagship GPT-4o, Sim-pleMem maintains its lead with an Average F1 of 39.06,
outperforming Mem0 (36.09) and A-Mem (33.45). These results confirm that Recursive Consolidation mechanism effectively distills high-density knowledge, enabling even smaller models equipped with SimpleMem to outperform larger models using traditional memory systems.
Token Efficiency. A key strength of SimpleMem lies in its inference-time efficiency. As reported in the rightmost columns of Tables 1 and 2, full-context approaches such as LOCOMO and MEMGPT consume approximately 16,900 tokens per query. In contrast, SimpleMem reduces token usage by roughly 30×, averaging 530–580 tokens per query. Furthermore, compared to optimized retrieval baselines like Mem0 (∼980 tokens) and A-Mem (∼1,200+ tokens), Sim-pleMem reduces token usage by 40-50% while delivering superior accuracy. For instance, on GPT-4.1-mini, Simple-Mem uses only 531 tokens to achieve state-of-the-art per-formance, whereas ReadAgent consumes more (643 tokens) but achieves far lower accuracy (7.16 F1). This validates the efficacy of our Entropy-based Filtering and Adaptive Pruning, which strictly control context bandwidth without sacrificing information density.
Performance on Smaller Models. Table 2 highlights the ability of SimpleMem to empower smaller parameter mod-els. On Qwen3-8b, SimpleMem achieves an impressive Average F1 of 33.45, significantly surpassing Mem0 (25.80) and LightMem (22.23). Crucially, a 3B-parameter model
5
SimpleMem: Efficient Lifelong Memory for LLM Agents
Table 2. Performance on the LoCoMo benchmark with Efficient Models (Small parameters). SimpleMem demonstrates robust performance even on 1.5B/3B models, often surpassing larger models using baseline memory systems.
Model Method MultiHop Temporal OpenDomain SingleHop Average Token F1 BLEU F1 BLEU F1 BLEU F1 BLEU F1 BLEU Cost
Qwen2.5-1.5b
LoCoMo 9.05 6.55 4.25 4.04 9.91 8.50 11.15 8.67 8.59 6.94 16,910 ReadAgent 6.61 4.93 2.55 2.51 5.31 12.24 10.13 7.54 6.15 6.81 752 MemoryBank 11.14 8.25 4.46 2.87 8.05 6.21 13.42 11.01 9.27 7.09 284 MemGPT 10.44 7.61 4.21 3.89 13.42 11.64 9.56 7.34 9.41 7.62 16,953 A-Mem 18.23 11.94 24.32 19.74 16.48 14.31 23.63 19.23 20.67 16.31 1,300 LightMem 16.43 11.39 22.92 18.56 15.06 11.23 23.28 19.24 19.42 15.11 605 Mem0 20.18 14.53 27.42 22.14 19.83 15.68 27.63 23.42 23.77 18.94 942 SimpleMem 21.85 16.10 29.12 23.50 21.05 16.80 28.90 24.50 25.23 20.23 678
Qwen2.5-3b
LoCoMo 4.61 4.29 3.11 2.71 4.55 5.97 7.03 5.69 4.83 4.67 16,910 ReadAgent 2.47 1.78 3.01 3.01 5.57 5.22 3.25 2.51 3.58 3.13 776 MemoryBank 3.60 3.39 1.72 1.97 6.63 6.58 4.11 3.32 4.02 3.82 298 MemGPT 5.07 4.31 2.94 2.95 7.04 7.10 7.26 5.52 5.58 4.97 16,961 A-Mem 12.57 9.01 27.59 25.07 7.12 7.28 17.23 13.12 16.13 13.62 1,137 LightMem 16.43 11.39 6.92 4.56 8.06 7.23 18.28 15.24 12.42 9.61 605 Mem0 16.89 11.54 8.52 6.23 10.24 8.82 16.47 12.43 13.03 9.76 965 SimpleMem 17.03 11.87 21.47 19.50 12.52 10.19 20.90 18.01 17.98 14.89 572
Qwen3-8b
LoCoMo 13.50 9.20 6.80 5.50 10.10 8.80 14.50 11.20 11.23 8.68 16,910 ReadAgent 7.20 5.10 3.50 3.10 5.50 5.40 8.10 6.20 6.08 4.95 721 MemoryBank 9.50 7.10 3.80 2.50 7.50 6.50 9.20 7.50 7.50 5.90 287 MemGPT 14.20 9.80 5.50 4.20 12.50 10.80 11.50 9.10 10.93 8.48 16,943 A-Mem 20.50 13.80 22.50 18.20 13.20 10.50 26.80 21.50 20.75 16.00 1,087 LightMem 18.53 14.23 26.78 21.52 14.12 11.24 29.48 23.83 22.23 17.71 744 Mem0 22.42 16.83 32.48 26.13 15.23 12.54 33.05 27.24 25.80 20.69 1,015 SimpleMem 28.97 24.93 42.85 36.49 15.35 13.9 46.62 40.69 33.45 29.00 621
Qwen3-1.7b
LoCoMo 10.28 8.82 6.45 5.78 10.42 9.02 11.16 10.35 9.58 8.49 16,910 ReadAgent 7.50 5.60 3.15 2.95 6.10 12.45 10.80 8.15 6.89 7.29 784 MemoryBank 11.50 8.65 4.95 3.20 8.55 6.80 13.90 11.50 9.73 7.54 290 MemGPT 11.50 8.20 4.65 4.10 13.85 11.90 10.25 7.85 10.06 8.01 16,954 A-Mem 18.45 11.80 25.82 18.45 10.90 9.95 21.58 16.72 19.19 14.23 1,258 LightMem 14.84 11.56 9.35 7.85 13.76 10.59 28.14 22.89 16.52 13.22 679 Mem0 18.23 13.44 18.54 14.22 16.82 13.54 31.15 26.42 21.19 16.91 988 SimpleMem 20.85 15.42 26.75 18.63 17.92 14.15 32.85 26.46 24.59 18.67 730
(Qwen2.5-3b) paired with SimpleMem achieves 17.98 F1, outperforming the same model with Mem0 (13.03) by nearly 5 points. Even on the extremely lightweight Qwen2.5-1.5b, SimpleMem maintains robust performance (25.23 F1), beat-ing larger models using inferior memory strategies (e.g., Qwen3-1.7b with Mem0 scores 21.19).
Robustness Across Task Types. Breaking down perfor-mance by task, SimpleMem demonstrates balanced capa-bilities. In SingleHop QA, it consistently leads (e.g., 51.12 F1 on GPT-4.1-mini), proving precision in factual retrieval. In complex MultiHop scenarios, SimpleMem significantly outperforms Mem0 and LightMem on GPT-4.1-mini, in-dicating that our Molecular Representations successfully bridge disconnected facts, enabling deep reasoning without the need for expensive iterative retrieval loops.
3.3. Efficiency Analysis
We conduct a comprehensive evaluation of computational efficiency, examining both end-to-end system latency and the scalability of memory indexing and retrieval. To assess practical deployment viability, we measured the full lifecy-cle costs on the LoCoMo-10 dataset using GPT-4.1-mini.
As illustrated in Table 3, SimpleMem exhibits superior ef-ficiency across all operational phases. In terms of memory construction, our system achieves the fastest processing speed at 92.6 seconds per sample. This represents a dra-matic improvement over existing baselines, outperforming Mem0 by approximately 14× (1350.9s) and A-Mem by over 50× (5140.5s). This massive speedup is directly at-tributable to our Semantic Structured Compression pipeline, which processes data in a streamlined single pass, thereby avoiding the complex graph updates required by Mem0 or the iterative summarization overheads inherent to A-Mem.
Beyond construction, SimpleMem also maintains the low-
6
SimpleMem: Efficient Lifelong Memory for LLM Agents
est retrieval latency at 388.3 seconds per sample, which is approximately 33% faster than LightMem and Mem0. This gain arises from the adaptive retrieval mechanism, which dynamically limits retrieval scope and prioritizes high-level abstract representations before accessing fine-grained details. By restricting retrieval to only the most relevant memory entries, the system avoids the expensive neighbor traversal and expansion operations that commonly dominate the latency of graph-based memory systems.
When considering the total time-to-insight, SimpleMem achieves a 4× speedup over Mem0 and a 12× speedup over A-Mem. Crucially, this efficiency does not come at the expense of performance. On the contrary, SimpleMem achieves the highest Average F1 among all compared meth-ods. These results support our central claim that structured semantic compression and adaptive retrieval produce a more compact and effective reasoning substrate than raw context retention or graph-centric memory designs, enabling a supe-rior balance between accuracy and computational efficiency.
Table 3. Comparison of construction time, retrieval time, total experiment time, and average F1 score across different memory systems (tested on LoCoMo-10 with GPT-4.1-mini).
Model Construction Time Retrieve Time Total Time Average F1
A-mem 5140.5s 796.7s 5937.2s 32.58 Lightmem 97.8s 577.1s 675.9s 24.63 Mem0 1350.9s 583.4s 1934.3s 34.20
SimpleMem 92.6s 388.3s 480.9s 43.24
3.4. Ablation Study
To verify the claims that specific cognitive mechanisms cor-respond to computational gains, we conducted a component-wise ablation study using the GPT-4.1-mini backend. We investigate the contribution of three key components: (1) Semantic Structured Compression , (2) Recursive Consoli-dation, and (3) Adaptive Query-Aware Retrieval. The results are summarized in Table 4.
Impact of Semantic Structured Compression. Replacing the proposed compression pipeline with standard chunk-based storage leads to a substantial degradation in temporal reasoning performance. Specifically, removing semantic structured compression reduces the Temporal F1 by 56.7%, from 58.62 to 25.40. This drop indicates that without con-text normalization steps such as resolving coreferences and converting relative temporal expressions into absolute times-tamps, the retriever struggles to disambiguate events along the timeline. As a result, performance regresses to levels comparable to conventional retrieval-augmented generation systems that rely on raw or weakly structured context.
Impact of Recursive Consolidation. Disabling the back-ground consolidation process results in a 31.3% decrease in multi-hop reasoning performance. Without consolidat-
ing related memory units into higher-level abstract repre-sentations, the system must retrieve a larger number of fragmented entries during reasoning. This fragmentation increases context redundancy and exhausts the available context window in complex queries, demonstrating that re-cursive consolidation is essential for synthesizing dispersed evidence into compact and informative representations.
Impact of Adaptive Query-Aware Retrieval. Removing the adaptive retrieval mechanism and reverting to fixed-depth retrieval primarily degrades performance on open-domain and single-hop tasks, with drops of 26.6% and 19.4%, respectively. In the absence of query-aware adjust-ment, the system either retrieves insufficient context for entity-specific queries or introduces excessive irrelevant in-formation for simple queries. These results highlight the importance of dynamically modulating retrieval scope to balance relevance and efficiency during inference.
3.5. Case Study: Long-Term Temporal Grounding
To illustrate how SimpleMem handles long-horizon conver-sational history, Figure 3 presents a representative multi-session example spanning two weeks and approximately 24,000 raw tokens. SimpleMem filters low-information dia-logue during ingestion and retains only high-utility memory entries, reducing the stored memory to about 800 tokens without losing task-relevant content.
Temporal Normalization. Relative temporal expressions such as last week” and yesterday” refer to different absolute times across sessions. SimpleMem resolves it into absolute timestamps at memory construction time, ensuring consis-tent temporal grounding over long interaction gaps.
Precise Retrieval. When queried about Sarah’s past art-works, the adaptive retrieval mechanism combines semantic relevance with symbolic constraints to exclude unrelated activities and retrieve only temporally valid entries. The system correctly identifies relevant paintings while ignor-ing semantically related but irrelevant topics. This example demonstrates how structured compression, temporal nor-malization, and adaptive retrieval jointly enable reliable long-term reasoning under extended interaction histories.
4. Related Work Memory Systems for LLM Agents. Recent approaches manage memory through virtual context or structured repre-sentations. Virtual context methods, including MEMGPT (Packer et al., 2023), MEMORYOS (Kang et al., 2025), and SCM (Wang et al., 2023), extend interaction length via pag-ing or stream-based controllers (Wang et al., 2024b) but typically store raw conversation logs, leading to redundancy and increasing processing costs. In parallel, structured and graph-based systems, such as MEMORYBANK (Zhong et al.,
7
https://lh3.googleusercontent.com/notebooklm/AG60hOrXJ0OWsSw_daKSSISjum9vDnSyk5LurKgbLKqnk_uFRi22HYvKmADisd6H5drZbuUMDWo-0a_X3MIlv5bJ1fi7nu-I6HIuhwVsoiCBtVuHfl7Dfwh0Q0hdXv_XmdrJIfqupcxM=w63-h77-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOpL7IefGYfT2lydbmcT0SvyVoE36oDMylCEs-KXgmVtwAMqsz2Cl9zjgIvTyGSKdsB7GQHd9zUOxjxnwO0ikJEzjaF8pOD-FV34YTwbmXLWyieLw5j67G2mHLz9HC5wn6lyxEegZg=w161-h165-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOoCcLNAnLCiFW0UIo3eS-t7iCif68IzIphXi58LrieK_0kR3SunzgQAAy3z512fvQtxFn_upgik_pyGWZ_7OPaPh8CN457PnQRX2nlDzHE_FiFlJ3_jUkzRg0xHRoOkpUxOTOcj4g=w156-h166-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOqfPavRubt4u5VDwlB7yVSK1rttj_GPbEyfmeA4cuf8K8ufM4OAy22DMYUMlLeXZhxJ4onecpGIniq9-AOA18XmMeJIrPhQ7VBAg-gkYudSDGITSY-BCnG7sbHn_hDBThfZeCajQQ=w278-h398-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOoJXF7gkBc6E7nthw_xf_y3tsbRwAjgM4mQYTx-F4a07pffIIqfreR1rmeXly9OaWnklx42KFS5aNu15mvsFy8GBV46sbRrvukaWzr7dmqcJXm40_2h_Oj0D3_bJV7iU5qUtpYo2A=w54-h42-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOq5gzLGLhBdXrvv6cINYHHhgVcrV4caZ2ee37DpwyE4jb2IXrvsZWtcuZFXMPq50H7guEkwXrDuZl-u0d3UrbxQkVmLcxlJ-uEYps2oCtF26kpc4B_0kuNlhwLtc2dekbgdnvuxoA=w120-h128-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOqJ3-L6ORQQWd3EX_NMAL-DJADMo2-_Xo_ji0HmU4BcjHvFN6FTgcNDDPMV_mLOjXe5O_J0SH0t9duzwziTNdEEhgSr353BAcXM88UuB3n2ifLiE_gskp8BAnjEvQgHIZukQYga=w86-h106-v0
https://lh3.googleusercontent.com/notebooklm/AG60hOoIs4jt3yTuUHZcUtd4v_T-eOfhl5km4GWiIDn9CTODKcCEvAWXe5lw_ShW7Inr04emu0Au8HV1bq7DFoPljIJ-HQsWd6LOhIAP1il2DOIVkQLJsob7zMAHT4t_QuUhxdQVgFL5WQ=w161-h165-v0
SimpleMem: Efficient Lifelong Memory for LLM Agents
Table 4. Full Ablation Analysis with GPT-4.1-mini backend. The "Diff" columns indicate the percentage drop relative to the full SimpleMem model. The results confirm that each stage contributes significantly to specific reasoning capabilities.
Configuration Multi-hop Temporal Open Domain Single Hop Average F1 Diff F1 Diff F1 Diff F1 Diff F1 Diff
Full SimpleMem 43.46 - 58.62 - 19.76 - 51.12 - 43.24 -
w/o Atomization 34.20 (↓21.325.40 (↓56.717.50 (↓11.448.05 (↓6.031.29 (↓27.6w/o Consolidation 29.85 (↓31.355.10 (↓6.018.20 (↓7.949.80 (↓2.638.24 (↓11.6w/o Adaptive Pruning 38.60 (↓11.256.80 (↓3.114.50 (↓26.641.20 (↓19.437.78 (↓12.6
Raw Input: Multi-Session Dialogues
Session 1 (2023-07-02 14:30)
Session 2 (2023-07-15 19:20)
Raw Token Count: ~24,000 tokens
[14:30] Sarah: Hey Emma! Good to see you! How have you been? [14:31] Emma: Hey Sarah! I'm swamped with the kids & work. What's up with you? [14:32] Sarah: I just signed up for a pottery class yesterday! It's like therapy for me. [14:33] Emma: Wow, that's cool! What made you try pottery? [14:34] Sarah: ...I made a black and white bowl in class... [14:36] Emma: ...You really put in the work. [14:39] Sarah: Actually, I painted a sunset with palm trees last week with my kids... [14:41] Sarah: We're planning to go camping in the mountains next month. [14:42] Emma: Sounds fun! Well, I gotta run. Talk soon! [14:43] Sarah: Bye! Talk to you later!
[19:20] Emma: Hey Sarah! How was your week? [19:21] Sarah: ...I took my kids to the Natural History Museum last Wednesday. They loved the dinosaur exhibit! [19:27] Sarah: I finished painting a horse portrait yesterday! It's for for my daughter's room - she's turning 8 next month on August 13th. [19:30] Sarah: ...We're having a birthday party at the park... [19:33] Sarah: We went camping at the beach last weekend! We roasted marshmallows, told stories around the campfire, and even saw shooting stars! [19:36] Sarah: ...The kids were in awe of the universe. We're planning another camping trip to the forest in September. [19:38] Emma: Sounds like you have a busy summer! Gotta go now, bye! [19:39] Sarah: Bye Emma! Let's catch up again soon!
SimpleMem Processing Pipeline: Three-Stage Architecture
1. Semantic Compression 2. Recursive Consolidation
3. Orthogonal Retrieval
Memory Database
3. Adaptive Retrieval
Entropy Filter
Filtered Out: "Hey Emma!", "Wow cool! ",
"That's great! ", "Gotta run", "Bye Emma!"
Atomized: M1:kids, M2:bowl,
M3:sunset, M4:camping,
M6:horse, M9:forest…
"yesterday"→"2023−07−01“"lastweek"→"2023−06−25“"mykids"→"Sarah 
′
 skids“
“nextmonth"→"August2023“"lastWed.“→"2023−07−12"
... Camping M4
M8 M9
Art Activities
M1 M2
M3 M6
Query: "What paintings has Sarah created?"
Query Analysis & Retrieval Planning
SEMANTIC Layer
Lexical Layer
Symbolic Layer
Hybrid Score Top-K Results
Result: M3,M6
Result: M3,M4
Result: M1, M3, M6
Token Reduction: ~800 tokens
Raw Input: Multi-Session Dialogues
Top-K Results
Final Retrieved Content
M3: sunset with palm trees
M1: Kids Activities
Final Answer
M6: horse portrait
Token Reduction: 30x
[2023-06-25] Sarah and her kids painted a
sunset with palm trees together.
[2023-07-14] Sarah finished painting a horse
portrait as a gift for her daughter.
[Consolidated] Sarah engages in painting as
both personal hobby and family activity.
A sunset with palm trees and a horse portrait
Figure 3. A Case of SimpleMem for Long-Term Multi-Session Dialogues. SimpleMem processes multi-session dialogues by filtering redundant content, normalizing temporal references, and organizing memories into compact representations. During retrieval, it adaptively combines semantic, lexical, and symbolic signals to select relevant entries.
2024), MEM0 (Dev & Taranjeet, 2024), ZEP (Rasmussen et al., 2025), A-MEM (Xu et al., 2025), and O-MEM (Wang et al., 2025), impose structural priors to improve coherence but still rely on raw or minimally processed text, preserving referential and temporal ambiguities that degrade long-term retrieval. In contrast, SimpleMem adopts a semantic com-pression mechanism that converts dialogue into independent, self-contained facts, explicitly resolving referential and tem-poral ambiguities prior to storage.
Context Management and Retrieval Efficiency. Beyond memory storage, efficient access to historical information remains a core challenge. Existing approaches primarily rely on either long-context models or retrieval-augmented generation (RAG). Although recent LLMs support extended context windows (OpenAI, 2025; Deepmind, 2025; An-thropic, 2025), and prompt compression methods aim to reduce costs (Jiang et al., 2023a; Liskavetsky et al., 2025), empirical studies reveal the “Lost-in-the-Middle” effect (Liu et al., 2023; Kuratov et al., 2024), where reasoning performance degrades as context length increases, along-side prohibitive computational overhead for lifelong agents. RAG-based methods (Lewis et al., 2020; Asai et al., 2023; Jiang et al., 2023b), including structurally enhanced vari-
ants such as GRAPHRAG (Edge et al., 2024; Zhao et al., 2025) and LIGHTRAG (Guo et al., 2024), decouple memory from inference but are largely optimized for static knowl-edge bases, limiting their effectiveness for dynamic, time-sensitive episodic memory. In contrast, SimpleMem im-proves retrieval efficiency through Adaptive Pruning and Retrieval, jointly leveraging semantic, lexical, and metadata signals to enable precise filtering by entities and timestamps, while dynamically adjusting retrieval depth based on query complexity to minimize token usage.
5. Conclusion We introduce SimpleMem, an efficient memory architecture governed by the principle of Semantic Lossless Compres-sion. By reimagining memory as a metabolic process, Sim-pleMem implements a dynamic continuum: Semantic Struc-tured Compression to filter noise at the source, Recursive Consolidation to evolve fragmented facts into high-order molecular insights, and Adaptive Spatial Pruning to dynam-ically modulate retrieval bandwidth. Empirical evaluation on the LoCoMo benchmark demonstrates the effectiveness and efficiency of SimpleMem.
8
SimpleMem: Efficient Lifelong Memory for LLM Agents
Acknowledgement This work is partially supported by Amazon Research Award, Cisco Faculty Research Award, and Coefficient Giv-ing.
References Anthropic. Claude 3.7 sonnet and claude code. https://www.anthropic.com/news/ claude-3-7-sonnet, 2025.
Asai, A., Wu, Z., Wang, Y., Sil, A., and Hajishirzi, H. Self-rag: Learning to retrieve, generate, and critique through self-reflection. arXiv preprint arXiv:2310.11511, 2023.
Deepmind, G. Gemini 2.5: Our most intelligent AI model — blog.google. https://blog. google/technology/google-deepmind/ gemini-model-thinking-updates-march-2025/ #gemini-2-5-thinking, 2025. Accessed: 2025-03-25.
Dev, K. and Taranjeet, S. mem0: The memory layer for ai agents. https://github.com/mem0ai/mem0, 2024.
Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., Truitt, S., and Larson, J. From local to global: A graph rag approach to query-focused summarization. arXiv preprint arXiv:2404.16130, 2024.
Fang, J., Deng, X., Xu, H., Jiang, Z., Tang, Y., Xu, Z., Deng, S., Yao, Y., Wang, M., Qiao, S., et al. Lightmem: Lightweight and efficient memory-augmented generation. arXiv preprint arXiv:2510.18866, 2025.
Guo, Z., Xia, L., Yu, Y., Ao, T., and Huang, C. Lightrag: Simple and fast retrieval-augmented generation. arXiv preprint arXiv:2410.05779, 2024.
Hu, Y., Liu, S., Yue, Y., Zhang, G., Liu, B., Zhu, F., Lin, J., Guo, H., Dou, S., Xi, Z., et al. Memory in the age of ai agents. arXiv preprint arXiv:2512.13564, 2025.
Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., and Qiu, L. Llmlin-gua: Compressing prompts for accelerated inference of large language models. arXiv preprint arXiv:2310.05736, 2023a.
Jiang, Z., Xu, F. F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., and Neubig, G. Active retrieval augmented generation. arXiv preprint arXiv:2305.06983, 2023b.
Kang, J., Ji, M., Zhao, Z., and Bai, T. Memory os of ai agent. arXiv preprint arXiv:2506.06326, 2025.
Kumaran, D., Hassabis, D., and McClelland, J. L. What learning systems do intelligent agents need? complemen-tary learning systems theory updated. Trends in cognitive sciences, 20(7):512–534, 2016.
Kuratov, Y. et al. In case of context: Investigating the effects of long context on language model performance. arXiv preprint, 2024.
Lee, K.-H., Chen, X., Furuta, H., Canny, J., and Fischer, I. A human-inspired reading agent with gist memory of very long contexts. arXiv preprint arXiv:2402.09727, 2024.
Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., et al. Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in Neural Information Pro-cessing Systems, 33:9459–9474, 2020.
Li, Z., Song, S., Wang, H., Niu, S., Chen, D., Yang, J., Xi, C., Lai, H., Zhao, J., Wang, Y., Ren, J., Lin, Z., Huo, J., Chen, T., Chen, K., Li, K.-R., Yin, Z., Yu, Q., Tang, B., Yang, H., Xu, Z., and Xiong, F. Memos: An operating system for memory-augmented generation (mag) in large language models. ArXiv, abs/2505.22101, 2025. URL https://api.semanticscholar. org/CorpusID:278960153.
Liskavetsky, A. et al. Compressor: Context-aware prompt compression for enhanced llm inference. arXiv preprint, 2025.
Liu, J., Xiong, K., Xia, P., Zhou, Y., Ji, H., Feng, L., Han, S., Ding, M., and Yao, H. Agent0-vl: Exploring self-evolving agent for tool-integrated vision-language reason-ing. arXiv preprint arXiv:2511.19900, 2025.
Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilac-qua, M., Petroni, F., and Liang, P. Lost in the middle: How language models use long contexts. arXiv preprint arXiv:2307.03172, 2023.
Maharana, A., Lee, D.-H., Tulyakov, S., Bansal, M., Bar-bieri, F., and Fang, Y. Evaluating very long-term con-versational memory of llm agents, 2024. URL https: //arxiv.org/abs/2402.17753.
OpenAI. Introducing gpt-5. https://openai.com/ index/introducing-gpt-5/, 2025.
Ouyang, S., Yan, J., Hsu, I., Chen, Y., Jiang, K., Wang, Z., Han, R., Le, L. T., Daruki, S., Tang, X., et al. Rea-soningbank: Scaling agent self-evolving with reasoning memory. arXiv preprint arXiv:2509.25140, 2025.
Packer, C., Fang, V., Patil, S. G., Lin, K., Wood-ers, S., and Gonzalez, J. Memgpt: Towards llms as operating systems. ArXiv, abs/2310.08560,
9
SimpleMem: Efficient Lifelong Memory for LLM Agents
2023. URL https://api.semanticscholar. org/CorpusID:263909014.
Qiu, J., Qi, X., Zhang, T., Juan, X., Guo, J., Lu, Y., Wang, Y., Yao, Z., Ren, Q., Jiang, X., et al. Alita: Generalist agent enabling scalable agentic reasoning with minimal predefinition and maximal self-evolution. arXiv preprint arXiv:2505.20286, 2025.
Rasmussen, P., Paliychuk, P., Beauvais, T., Ryan, J., and Chalef, D. Zep: a temporal knowledge graph architecture for agent memory. arXiv preprint arXiv:2501.13956, 2025.
Tang, X., Qin, T., Peng, T., Zhou, Z., Shao, D., Du, T., Wei, X., Xia, P., Wu, F., Zhu, H., et al. Agent kb: Leveraging cross-domain experience for agentic problem solving. arXiv preprint arXiv:2507.06229, 2025.
Team, T. D., Li, B., Zhang, B., Zhang, D., Huang, F., Li, G., Chen, G., Yin, H., Wu, J., Zhou, J., et al. Tongyi deepre-search technical report. arXiv preprint arXiv:2510.24701, 2025.
Tu, A., Xuan, W., Qi, H., Huang, X., Zeng, Q., Talaei, S., Xiao, Y., Xia, P., Tang, X., Zhuang, Y., et al. Position: The hidden costs and measurement gaps of reinforce-ment learning with verifiable rewards. arXiv preprint arXiv:2509.21882, 2025.
Wang, B., Liang, X., Yang, J., Huang, H., Wu, S., Wu, P., Lu, L., Ma, Z., and Li, Z. Enhancing large language model with self-controlled memory framework. arXiv preprint arXiv:2304.13343, 2023.
Wang, P., Tian, M., Li, J., Liang, Y., Wang, Y., Chen, Q., Wang, T., Lu, Z., Ma, J., Jiang, Y. E., et al. O-mem: Omni memory system for personalized, long horizon, self-evolving agents. arXiv e-prints, pp. arXiv–2511, 2025.
Wang, T., Tao, M., Fang, R., Wang, H., Wang, S., Jiang, Y. E., and Zhou, W. Ai persona: Towards life-long per-sonalization of llms. arXiv preprint arXiv:2412.13103, 2024a.
Wang, Y. and Chen, X. Mirix: Multi-agent memory system for llm-based agents. arXiv preprint arXiv:2507.07957, 2025.
Wang, Z. Z., Mao, J., Fried, D., and Neubig, G. Agent workflow memory. arXiv preprint arXiv:2409.07429, 2024b.
Xia, P., Zeng, K., Liu, J., Qin, C., Wu, F., Zhou, Y., Xiong, C., and Yao, H. Agent0: Unleashing self-evolving agents from zero data via tool-integrated reasoning. arXiv preprint arXiv:2511.16043, 2025.
Xu, W., Liang, Z., Mei, K., Gao, H., Tan, J., and Zhang, Y. A-mem: Agentic memory for llm agents. ArXiv, abs/2502.12110, 2025. URL https: //api.semanticscholar.org/CorpusID: 276421617.
Yan, B., Li, C., Qian, H., Lu, S., and Liu, Z. Gen-eral agentic memory via deep research. arXiv preprint arXiv:2511.18423, 2025.
Yang, B., Xu, L., Zeng, L., Liu, K., Jiang, S., Lu, W., Chen, H., Jiang, X., Xing, G., and Yan, Z. Contextagent: Context-aware proactive llm agents with open-world sen-sory perceptions. arXiv preprint arXiv:2505.14668, 2025.
Zhao, Y., Zhu, J., Guo, Y., He, K., and Li, X. Eˆ 2graphrag: Streamlining graph-based rag for high efficiency and ef-fectiveness. arXiv preprint arXiv:2505.24226, 2025.
Zhong, W., Guo, L., Gao, Q., Ye, H., and Wang, Y. Memo-rybank: Enhancing large language models with long-term memory. In Proceedings of the AAAI Conference on Arti-ficial Intelligence, volume 38, pp. 19724–19731, 2024.
10
SimpleMem: Efficient Lifelong Memory for LLM Agents
A. Detailed System Prompts To ensure full reproducibility of the SimpleMem pipeline, we provide the exact system prompts used in the key process-ing stages. All prompts are designed to be model-agnostic but were optimized for GPT-4o-mini in our experiments to ensure cognitive economy.
A.1. Stage 1: Semantic Structured Compression Prompt
This prompt performs entropy-aware filtering and context normalization. Its goal is to transform raw dialogue win-dows into compact, context-independent memory units while excluding low-information interaction content.
Listing 1. Prompt for Semantic Structured Compression and Nor-malization.
You are a memory encoder in a long-term memory system. Your task is to transform raw conversational input into compact, self-contained memory units.
INPUT METADATA: Window Start Time: {window_start_time} (ISO
8601) Participants: {speakers_list}
INSTRUCTIONS: 1. Information Filtering:
- Discard social filler, acknowledgements, and conversational routines that introduce no new
factual or semantic information. - Discard redundant confirmations unless
they modify or finalize a decision. - If no informative content is present,
output an empty list.
2. Context Normalization: - Resolve all pronouns and implicit
references into explicit entity names.
- Ensure each memory unit is interpretable without access to prior dialogue.
3. Temporal Normalization: - Convert relative temporal expressions
(e.g., "tomorrow", "last week") into absolute ISO 8601 timestamps using
the window start time.
4. Memory Unit Extraction: - Decompose complex utterances into
minimal, indivisible factual statements.
INPUT DIALOGUE: {dialogue_window}
OUTPUT FORMAT (JSON): { "memory_units": [
{ "content": "Alice agreed to meet Bob
at the Starbucks on 5th Avenue on 2025-11-20T14:00:00.",
"entities": ["Alice", "Bob", " Starbucks", "5th Avenue"],
"topic": "Meeting Planning", "timestamp": "2025-11-20T14:00:00", "salience": "high"
} ]
}
A.2. Stage 2: Adaptive Retrieval Planning Prompt
This prompt analyzes the user query prior to retrieval. Its purpose is to estimate query complexity and generate a struc-tured retrieval plan that adapts retrieval scope accordingly.
Listing 2. Prompt for Query Analysis and Adaptive Retrieval Planning.
Analyze the following user query and generate a retrieval plan. Your objective is to retrieve sufficient information while minimizing unnecessary context usage.
USER QUERY: {user_query}
INSTRUCTIONS: 1. Query Complexity Estimation:
- Assign "LOW" if the query can be answered via direct fact lookup or a single memory unit.
- Assign "HIGH" if the query requires aggregation across multiple events, temporal comparison, or synthesis of patterns.
2. Retrieval Signals: - Lexical layer: extract exact keywords
or entity names. - Temporal layer: infer absolute time
ranges if relevant. - Semantic layer: rewrite the query into
a declarative form suitable for semantic matching.
OUTPUT FORMAT (JSON): {
"complexity": "HIGH", "retrieval_rationale": "The query
requires reasoning over multiple temporally separated events.",
"lexical_keywords": ["Starbucks", "Bob"], "temporal_constraints": { "start": "2025-11-01T00:00:00", "end": "2025-11-30T23:59:59"
}, "semantic_query": "The user is asking
about the scheduled meeting with Bob, including location and time."
11
SimpleMem: Efficient Lifelong Memory for LLM Agents
}
A.3. Stage 3: Reconstructive Synthesis Prompt
This prompt guides the final answer generation using re-trieved memory. It combines high-level abstract representa-tions with fine-grained factual details to produce a grounded response.
Listing 3. Prompt for Reconstructive Synthesis (Answer Genera-tion).
You are an assistant with access to a structured long-term memory.
USER QUERY: {user_query}
RETRIEVED MEMORY (Ordered by Relevance):
[ABSTRACT REPRESENTATIONS]: {retrieved_abstracts}
[DETAILED MEMORY UNITS]: {retrieved_units}
INSTRUCTIONS: 1. Hierarchical Reasoning:
- Use abstract representations to capture recurring patterns or general user preferences.
- Use detailed memory units to ground the response with specific facts.
2. Conflict Handling: - If inconsistencies arise, prioritize
the most recent memory unit. - Optionally reference abstract patterns
when relevant.
3. Temporal Consistency: - Ensure all statements respect the
timestamps provided in memory.
4. Faithfulness: - Base the answer strictly on the
retrieved memory. - If required information is missing,
respond with: "I do not have enough information in my memory."
FINAL ANSWER:
B. Extended Implementation Details and Experiments
B.1. Hyperparameter Configuration
Table 6 summarizes the hyperparameters used to obtain the results reported in Section 3. These values were selected to balance memory compactness and retrieval recall, with
particular attention to the thresholds governing semantic structured compression and recursive consolidation.
B.2. Hyperparameter Sensitivity Analysis
To assess the effectiveness of semantic structured compres-sion and to motivate the design of adaptive retrieval, we an-alyze system sensitivity to the number of retrieved memory entries (k).We vary kfrom 1 to 20 and report the average F1 score on the LoCoMo benchmark using the GPT-4.1-mini backend.
Table 5. Performance sensitivity to retrieval count (k).Simple-Mem demonstrates "Rapid Saturation," reaching near-optimal per-formance at k= 3 (42.85) compared to its peak at k= 10 (43.45). This validates the high information density of Atomic Entries, proving that huge context windows are often unnecessary for accu-racy.
Method Top−kRetrieved Entries k=1k=3k=5k=10k=20
ReadAgent 6.12 8.45 9.18 8.92 8.50 MemGPT 18.40 22.15 25.59 24.80 23.10 SimpleMem 35.20 42.85 43.24 43.45 43.40
Table 5 provides two key observations. First, rapid perfor-mance saturation is observed at low retrieval depth. Simple-Mem achieves strong performance with a single retrieved entry (35.20 F1) and reaches approximately 99% of its peak performance at k= 3. This behavior indicates that semantic structured compression produces memory units with high in-formation content, often sufficient to answer a query without aggregating many fragments.
Second, robustness to increased retrieval depth distinguishes SimpleMem from baseline methods. While approaches such as MemGPT experience performance degradation at larger k,SimpleMem maintains stable accuracy even when retrieving up to 20 entries. This robustness enables adaptive retrieval to safely expand context for complex reasoning tasks without introducing excessive irrelevant information.
12
SimpleMem: Efficient Lifelong Memory for LLM Agents
Table 6. Detailed hyperparameter configuration for SimpleMem. The system employs adaptive thresholds to balance memory compactness and retrieval effectiveness.
Module Parameter Value / Description
Stage 1: Semantic Structured Compression
Window Size (W) 10 turns Sliding Stride 5 turns (50% overlap) Information Threshold (τ) 0.35 (filters low-information interaction content) Model Backend gpt-4o-mini (temperature = 0.0) Coreference Scope Current window with up to two preceding turns Output Constraint Strict JSON schema enforced
Stage 2: Recursive Consolidation
Embedding Model text-embedding-3-small (1536 dimen-sions)
Consolidation Threshold (τcluster)0.85 (triggers abstraction over related memory units)
Temporal Decay (λ)0.1 (controls temporal influence during consolida-tion)
Vector Database LanceDB (v0.4.5) with IVF-PQ indexing Stored Metadata timestamp, entities, topic, salience
Stage 3: Adaptive Retrieval
Query Complexity Estimator gpt-4o-mini (classification head) Retrieval Range k∈[3,20] Minimum Depth (kmin)3 (symbolic and abstract-level retrieval) Maximum Depth (kmax)20 (expanded semantic retrieval) Re-ranking Disabled (multi-view score fusion applied directly)
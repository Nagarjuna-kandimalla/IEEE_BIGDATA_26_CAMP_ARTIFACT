Need An Experiment and explanation - NAE
Just Explanation - JE

- Reviewer - 1
    - Histroical read bytes will not tell us how new input data will effect execution [NAE]
        A. IF the saem workflows are run on teh same data multiple times, but how much on new data needs to be validated
        If i try to run these workflows again on new data, may be then, a short experiment may be not this much of data using camp, but new data for these workflows will tell us how much historical will give us the information.
            - A new data meeda run chestey workflows ni,appudu ablation of historical read data (C his) on this for workflows using camp : (A+H_p+C hat, A+H_p+H_c+C hat)
    - amount of data read does not necessarily correlate with peak memory usage [JE]
        - For example, a streaming program may read a large amount of data while maintaining a small memory footprint.
            A. I think i need to mention what kind of programs is this model useful for, for mainly ROI kind and which has mmap calls
    - Ask 1 : CAMP already uses historical peak-memory measurements, the paper needs to explain why historical file-data consumption provides significant additional predictive information.
        A. ablation test of H_c should be provided - Done [JE]
    - Ask 2:  paper should separately evaluate the benefits of historical file-data consumption measurements and the consumption prediction model
    *** Ablation experiments are needed ***
        A. ablation experiments of H_c and Chat need to be added. - Done [JE]
    - Ask 3: a simple allocator using historical peak-memory statistics from similar tasks.
        - reason : Given that scientific workflows often repeat the same application stages, a simple historical percentile with a safety margin could potentially provide good predictions
            A. a proof of experiment with a simple allocator and differences - [NAE]
        - The above is to justify the camp's complexity
    - Ask 4: a equal budgetted study comparision between sizey and CAMP to show that CAMP is not just a model which allocates more memory for removing under allocations
        A. Equal budgetted test are to be mentioned. - Done [JE]

- Reviewer - 2
    - Positive remarks

- Reviewer - 3
    - falls short in the discussion of the actual implementation of the proposed methodology and experimental evaluation. 
        A. Have to check why- but not needed now 
    - The description of the experimental evaluation is often unclear.
        A. Not needed???
    - final experiment presented in Section 5-E is weak, not representative of diverse scientific workflows, as well as appears to contradict earlier findings in the paper.
        A.  1. contradiction is first time underallocations issue [JE]
            2. May be more diff scientific workflows are needed to run with camp model [NAE]
    - How scopes are defined, how are they matched for compatibility when a pending task arrives with the historical tasks. How the scopes are evalauated in experiment evaluation section.
        A. need more information about scopes [JE]
    - The paper falls short in discussion of the actual implementation and in the experimental evaluation, as I set out below. The final experiment is weak and because of its specificity it does not convince that this method is worthwhile for wider application in (bioinformatics) workflows. 
        A. may be little focus on exp 5 (RQ 5)
    
    - Paper writing specifics:
        - It never fully became clear to me what an "multi-gate active learning selection policy" is. Section III-G is said to describe "the gates that determine the auditing policy". However, the word "gate" never occurs in this subsection.
            A. Not clearly explained about gates - but not required?? [JE]
        - EBPF , its integration with worjflows, workflow changes requried to incorporate ebpf, nextflow usage, and its its integration with CAMP.
            A. Explanation about these, seems like extra info [JE]
        - Matched offline cohort meaning in 4-a
            A. [JE]
        - Section IV-A: consider that this description of the various workloads is inaccessible to a more general BigData audience.
            A. What does this mean?
        - out of fold predictions explanation related to development predictions in iv - c
            A.  [JE]
        - Five questions instead of four 
            A. wil be removed

        - Section IV-D: Cov and MdAPE are not briefly described in the main text
            A. Have to remove the metrics, which are not told in the results
        - Section V-A: what is a "consumed-data signal" ?
            A. [JE]
        - Section V-A: what is the motivation for comparing to strace? strace cannot capture the same data? Why is this a good and representative comparison target for overhead?
            A. [JE]
        - Section V-B: erroneously refers to Figures 2a(a), 2b(b) and 2b(a).
            A. [JE]
        - Section V-B: where do the numbers for unused memory-time and total requested memory follow from? These are not shown in the referenced figure?
            A. Not in the figure but not necessary now
        -  Section V-C: what is "first-attempt coverage"? The number of tasks thatsucceed without OOM due to  underallocation?
            A. [JE]
        -  Section V-C: given that Sizey has a large number of underallocated tasks, does that mean that Sizey has a high task failure rate? Is this common for and to be expected from Sizey?
            A. [JE]
        - Section V-C: the authors seem to take for granted that CAMP uses significantly more reserved capacity than Sizey, even though in the Introduction it is pointed out that overestimation and conservative upper bounds should be avoided because these result in cluster inefficiency. Now, the question here is whether CAMP's higher reservations are really necessary. Are these conservative upper bounds or strict upper bounds to ensure that tasks will not fail due to OOM errors?
            A. Show how much more is the allocated memory from the exact requried memory for each taska nd get soem metric out of it to show that these are really necessary and how much is it necessary without calibration?
            [NAE]
        - Figure 3: the graph titles do not match the caption which is a little confusing. Moreover, the fact that for subgraph (c) the x-axis is different but with the same colors for the bars is more confusing. I also don't fully understand why the x-axis and the color bar legend have the same labels? Shouldn't the blue bar convey the Sizey baseline?
            A. [JE]
        - Section V-E: what is a "logical Bowtie2 task" in contrast to a default Bowtie2 task?
            A. [JE]
        - Section V-E: does each of the 6000 Bowtie2 tasks operate on the same data set, or on different data sets of different sizes?
            A. [JE]
        - Section V-E: am I correct in assuming that the Bowtie2 tasks are independent of each other? So, isn't this experiment more representative of a SLURM job array rather than a scientific workflow that commonly consists of different components?
            A. Need to understand what this bowtie does and are these independent of each other [JE]
        - Section V-E: how does Sizey perform on this benchmark? Why are no results reported for Sizey?
            A. Sizey on bow tie [NAE]
        - Section V-E: am I right in understanding that a single "cold run" was done, followed by a single "warm run"? Wouldn't it for a simple scenario like this be the case that simple manual memory profiling can also lead to significantly improved memory estimation settings? In other words, how does this experiment convey that CAMP is suited for more complicated workflows that are run repeatedly with varying data set sizes?
            A. Needd to experiment the same workflow on diff data sets using the cold run information and check if the prediction is worth [NAE]
        - Section V-E: so, in this case CAMP leads to a worse first-attempt coverage. In Section V-C you did, however, show that CAMP leads to significantly better first-attempt coverage and also higher reserved capacity. What is an explanation for that fact that in this experiment we see tighter and smaller memory allocations for a number of tasks? This result comes across as being a bit contradictory.
            A. so need to understand why the first attempt of offline experiment is better than first attempt of cold run, because of model trained on offline adn then used only certain set for testing in which it performed better? [JE]
        - Section VIII: "to safely reduce cluster overprovisioning at scale". Given the focus of the policy and paper on avoiding underallocation and the fact that one of the results of Section V-C is that CAMP needs larger memory reservations compared to Sizey, I am not sure whether I agree with this overall statement.
            A. [JE]
- Reviewer - 4
    - Questions
        1) CAMP underallocates fewer tasks at 50/50 and 85/15 but more at 30/70, 70/30, and 90/10. The 85/15 split also has high seed variation. This suggests the policy is not uniformly robust.
            A. true, work on model
        2) Compared with Sizey, CAMP’s request-to-peak ratio is 225.5% and unused memory time is 141.4%. This is a significant trade-off that must be considered.
            A. will add the equal budgeted analysis data here
        3) Evaluation focuses on bioinformatics workflows. It is unclear how well CAMP generalizes to other scientific domains, HPC workloads, or non-Nextflow pipelines.
            A. have to work on diff workflows [NAE]
        4) The first run uses a conservative default. The paper shows warm-run improvement but does not deeply analyze cold-start cost across diverse workflows.
            A. Online deployed cost on different workflows for cold start [NAE]
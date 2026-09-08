# Your team's maintenance context

Setup: incomplete

Replace the prompts below with your own paths and decisions, then set `Setup: ready`. The dispatcher refuses unattended work until this context is ready. Revisit it when priorities change.

## What matters now

Which business outcomes should maintenance protect? Name the important user journeys, current technical bottlenecks, and areas deliberately left alone. Explain the tradeoffs a cold session cannot infer from code.

## Sources of truth

Name the existing files that own coding conventions, architecture, domain behavior, testing, and review policy. Include the commands needed to validate changes. Reference existing guidance instead of copying it here.

## Skills and scope

Which menu skills are useful for this repository? Disable the others in config. For each enabled skill, name its target areas and the available evidence (timings, coverage, dependency advisories, design-system rules). Reuse your existing skills when they already do the job.

## Boundaries

Name additional excluded directories and operations. The shared contract already excludes auth, payments, personal-data handling, and migrations. For UI work, identify an authorized sandbox and permitted test actions, never credentials.

## Delivery

Name the ticketing tools and repository used by this installation. For a tracker other than GitHub Issues, adapt the binding in `.quota-burner/CONTRACT.md` before enabling runs. Specify the branch and PR conventions, available event subscriptions, and who reviews the results. Record the owner's authorization for unattended branches, commits, pushes, issues, and PRs; repository restrictions still take precedence.

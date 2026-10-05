Making Formal Spec
====================

I need help turning this project into a formal specification. There should be a markdown file which is formal specification, and it should have the musts and the wills and the shalls and the must nots and may's and shoulds and what-not, articulated in it, and ultimately it should work backwards and have essentially the same contents as the README, except it must highlight the hard requirements necessary in order to be conformant. And it should begin with the well-known file, and then the first element, the well-known file, is that you should have a federated payer identifier, and then it should say you must have the federated payer identifier, and then just link to the: "Generating federated identifier" markdown files.

There must be at least one Federated Payer Identifier (FPI), and each FPIs should be listed before the legacy payer identifiers. Every Legac payer identifier must reference one and only one parent_fpi_id. If Legacy identifiers that already exists for your payer company. And and then as it goes on through the requirements of well known file format.

The payer identifier that uniquely correctly identifies the payer and is used in commerce should be, or in claims or in commerce, and and is expected to be a mechanism by which the payer is looked up should be included with a secondary identifier listed in the identifier section of the well-known file. And then the plan groups are made up of objects that have plan identifiers, which are of course required. Each plan identifier must identify its parent FPI in the file. 

And then the plan, any plan name must have at least one plan level search match and the plan network, plan website is required and the plan name is required. and the plan ID is required. that is expected to be a randomly generated UUID, but it should be maintained over time and it should not be changed. Each year for the same plan, so that should be stable over time. And then every identifier for the plan should be listed in in the list of plan identifiers, and every one of them has to have the basic information:
- parent FPI
- the value
- the system
- the plan ID
- the plan name
- the plan website
- the plan level string
- search string matches (at least one)
- etc.
And then there should be one set of plan endpoints, and the plan endpoints should be all of the endpoints that the payer offers for the relevant plans and those mandated by CMS rules in general. If there are sandbox accounts, they have to be there.

There must be links to be links to the developer websites in the endpoint section as well.


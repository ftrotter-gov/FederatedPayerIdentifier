Raw Data Sources
==========================

This repo intends to reconcile data released in multiple different formats by multiple parties. 
Sometimes this will be accomplished using pull requests directly against the json files...

But there will also be cases where data processing is nessecary to convert the data from one format to another. 

This directory will contain both the data that is being sourced as well as the code needed to convert that data into the json formats. 

When the code is bespoke.. it will be in the same directory as the data itself. We will try to prefix reusable code with library_ to mark that can import multiple released datasets. 


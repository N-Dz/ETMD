# Project Overview

This project creates a tool for harvesting metadata.

It is based on this spec: @spec_project_instructor.pdf

# Architecture

- Input file -> LLM decided which extract tool to call -> tool return info -> Normalization -> output

# Coding Rules

- Spec suggest JS, we will use Python - BE + FE 
- Check for dead code and remove, explicitly stating why and where you have done so
- Write short, composable block of code and reuse code when possible 
- Ask for detailed guidance and answers when the task seems ambigious 
- Dublin Core metadata 

4thYearProject

Fourth-year Computer Science dissertation project investigating a provenance-aware authorisation architecture for LLM-based systems.

Overview

Modern LLM applications are vulnerable to privilege escalation through prompt injection and indirect influence attacks because they often execute actions using the authority of the application rather than the authority of the information that caused those actions.

This project investigates an alternative execution model in which every piece of information carries provenance, and every protected action is authorised according to the effective authority of all information that contributed to it.

The core hypothesis is that propagating provenance throughout execution and evaluating authorisation from that provenance can prevent unauthorised actions without relying on prompt filtering or trusted/untrusted input classifications.

Objectives

* Develop a provenance-aware execution model for LLM systems.
* Design an authorisation model based on provenance-derived authority.
* Support realistic enterprise authorisation policies inspired by AWS IAM, Google Cloud IAM and Microsoft Entra.
* Evaluate the architecture against prompt injection and related influence attacks.
* Produce a reference implementation demonstrating the proposed design.

Planned Architecture

src/
    fourth_year_project/
        core/
        execution/
        auth/
        policy/
        tools/
tests/
docs/
examples/

Development Principles

* Information is never classified as trusted or untrusted.
* Every artefact carries provenance.
* Provenance is propagated through every operation.
* Authorisation is evaluated immediately before protected actions.
* Policies are separated from execution semantics.
* Components should be independently testable.

Repository Status

🚧 Early development.

The initial implementation focuses on the core provenance data model before introducing execution graphs, authorisation and policy engines.

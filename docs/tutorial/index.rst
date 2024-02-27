Tutorial
========

In this tutorial, we are going to build a simple Todo app in a modular fashion. Modularization of such a trivial 
application seems like an overkill, but the goal of this tutorial is:

- to demonstrate the core features of *lato* in action, 
- how to decompose the application into independent, loosely coupled modules
- how to implement the interaction between the modules using messaging


In the process of designing a modular application, our goal is to divide the logic into modules - smaller units that exhibit high cohesion while maintaining low coupling between them.
We will explore the basics of making a module of an application. We will also learn how modules communicate with each other through events.

The *Todo* application is divided into the following modules:

- *Todos*: the core functionality related to creating and completing todos,
- *Analytics*: functionality related to gathering various stats,
- *Notifications*: functionality related to sending reminders and other notifications.

This tutorial is divided into the following parts:

..  toctree::
    :maxdepth: 3

    tutorial_01
    tutorial_02
    tutorial_03
    tutorial_04
    tutorial_05
    tutorial_06



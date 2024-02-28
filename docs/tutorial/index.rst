Tutorial
========

In this tutorial, we are going to build a simple Todo app in a modular fashion. Modularization of such a trivial 
application seems like an overkill, but the goal of this tutorial is to demonstrate:

- the core features of *lato* in action, 
- how to decompose the application into independent, loosely coupled modules,
- how the modules can interact between each other by exchanging messages.

In the process of designing a modular application, our goal is to split the logic into independent modules - smaller 
units that exhibit high cohesion while maintaining low coupling. We are aiming at such architecture, that will allow us
to split the monolith into microservices in the distant future.

The *Todo* application is divided into the following modules:

- *Todos* - the core functionality related to creating and completing todos,
- *Analytics* - contains functionality related to gathering various stats,
- *Notifications* - contains functionality related to sending reminders and push notifications.

This tutorial is divided into the following parts:

..  toctree::
    :maxdepth: 3

    tutorial_01
    tutorial_02
    tutorial_03
    tutorial_04
    tutorial_05
    tutorial_06



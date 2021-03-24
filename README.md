# Evaluating-Life-Insurance-Policies

Narrative

We would like to have an automated system that can evaluate life insurance policies. A life insurance policy, or simply policy, can have one holder (or insured), and has the properties defined in the policy worksheet.

A policy can have two payment schedules: DB and Premiums. The schedules are two time-series with year as unit and they represent future dollar amounts. You can find the DB and Premiums in their respective spreadsheets.

Each insured has a life expectancy that we estimate using population survival curves separated by binary gender. The survival curves can be found in the Survival worksheet.

Finally, a policy valuation is done using excel formulas as show in the Value worksheet. In this worksheet, you will find all the formulas you need to develop the API.

Please develop a python application that does the three calculations below:

Build a survival curve (column F in Value tab) for one individual. All variables that can change the survival curve should be parameterized
Calculate the total cashflow for a policy (column M in Value tab), with an option to include/exclude fees
Calculate the total value of all policies in the Policy tab at 12% discount rate (column O)
Keep in mind that the purpose of this exercise is to gauge your ability to design and build a python application using OOP, in order to automate tasks that are currently performed in MS Excel.

The areas considered when evaluating the solution are:

Design - is the code design appropriate for the data and problem it solves? (50%)
Simplicity - is the code simple to understand or too complex for what it does? (20%)
Repeatability - does the code execute successfully and seamlessly on another machine and with parameterized input values? (20%)
Functionality - does the code behave as intended? (10%)

# SIM Swap Fraud Detection
This repository contains prototype code I developed to map changes in transactional networks of telecoms subscribers immediately after swapping their SIMs.  

A SIM swap followed by a PIN reset is considered high risk activity in mobile fraud management. This Python program compares GSM mobile money transactions made before and after SIM swaps and PIN resets. It highlights unfamiliar transactions in red, and familiar ones in green. 

If a mobile user's transactions are all unfamiliar post SIM reset, it is highly likely that the user has obtained access to someone's phone fraudulently, and is attempting to empty the victim's mobile money account. Such transactions are usually made to mobile money merchants in an attempt to launder the funds. 

This code allows detection of SIM swap fraud in real time, as well as the ability to map money laundering networks for watchlisting purposes.  

 

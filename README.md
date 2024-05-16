# SportsSync Application

## Purpose of SportsSync

We were tired of the constant back and forth trying to find a substitute to fill in for our social sports team at UWA and having to fork out hefty forfeit fees. To eliminate this hassle, we created SportsSync, making it easier for teams to find substitutes and manage their events seamlessly.

SportsSync is a web-based platform, created using Flask, designed to connect sports enthusiasts by allowing them to browse, join, and create sports events in their community. It enables users to tailor their experience through customisable profiles and facilitates easy communication and management of events. This solution addresses the need for a centralised location where athletes of all levels can find and organise sports activities according to their preferences and skill levels.

## Group Members

| Student Name   | Student Number | Github Username |
| -------------- | -------------- | --------------- |
| Lauren Hart    | 23164229       | lauhart         |
| Declan Barrett | 23074941       | DeclanB1        |
| Edward Le      | 23020568       | edwardisintou   |
| Matthew Chew   | 22974046       | mattcw9090      |


## SportsSync Architecture

>TO_DO Short Description and Screenshot for Each

### Register New Account

### Login

### Post New Event

### Browse Events

### Update User Profile

### Update/Delete Existing Event

## Quick Start Guide

Follow these steps to get the Flask application running locally on your machine:

1. **Create and Activate a Virtual Environment**
   Open your terminal and run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install Required Dependencies**

```bash
pip3 install -r requirements.txt
```

3. **Create Secret Key**

   a) Create new .env file

   b) Generate secret key

   c) Save generated secret key to variable SECRET_KEY in .env

```python3
import os
os.urandom(24)
quit()
```

4. **Navigate the Source Directory**

```bash
cd src
```

5. **Launch Application**

```bash
python3 app.py #run with debug mode on
```

or

```bash
flask run #run with debug mode off
```

## How to run Tests

>TO_DO

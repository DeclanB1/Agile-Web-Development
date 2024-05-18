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

### Register New Account

![Screenshot 2024-05-18 at 2 27 25 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/903b668f-8771-451e-a005-6f6fd9293825)

_Note: not all fields are necessary some are optional for the user, and can be editted later on_

### Login

User is directed to Login Page

![Screenshot 2024-05-18 at 2 27 55 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/cb5d039f-e1f5-444a-ae7d-3bb7bef5edb5)

User is logged in (Introductory View is displayed)

![Screenshot 2024-05-18 at 2 44 16 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/75ccaa9b-e6d2-45fe-a21d-a4c1a770ebc8)

### Browse Events (Find Requests View)

Click "Browse Events" from the navigation bar

User can browse all existing event request posts 

_Note: User does not need to be logged in to view this page_

![331771291-c4d2ef6b-707b-40f9-abbe-75d260519acd](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/f2e8bd43-64ed-41a4-a04a-3fba06ccafe7)

By clicking on details, user can view specific event request details

![Screenshot 2024-05-18 at 2 30 01 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/3d983fba-73d6-47ff-886f-cecb48b0eeb5)

### Post New Event (Create Requests View)

Click "Post New Event" from the navigation bar

![Screenshot 2024-05-18 at 2 33 44 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/0df36c48-0a26-4075-b11d-49a2f7f2801f)

### Update User Profile (eg. add Profile Picture)

Click "My Profile" from the Navigation Bar

![Screenshot 2024-05-18 at 2 34 24 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/61aaeb75-0c86-4135-88a2-1311b09cef38)

Click on Profile Picture to edit

![Screenshot 2024-05-18 at 2 34 48 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/715c0001-9c2d-4c93-91f3-e8e8650a0a03)

Select "Choose File", followed by Uploaded Picture

![Screenshot 2024-05-18 at 2 35 52 pm](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/2eb2c14e-b70c-409b-b89d-8e9a852a6f63)

_Note: User can also update their profile information_

### Update/Delete Existing Event

User can view, update or delete their existing events

![331771712-69438838-a1c2-4a7d-97fe-23563d725dc7](https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/9fcfe71b-5aa3-48d0-8a1a-f33727e4cd6f)

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

   a) Create new file called ".env" 

   b) Generate unique secret key in the terminal

```python3
import os
os.urandom(24)
quit()
```

   c) Save generated secret key to variable SECRET_KEY in .env

<img width="1214" alt="Screenshot 2024-05-17 at 2 50 10 pm" src="https://github.com/DeclanB1/Agile-Web-Development/assets/128463081/e2c0b633-4d24-4380-95c0-ff09bf7146ee">

Sample SECRET_KEY saved to .env file

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

```bash
cd src
python -m unittest test_app.py                                                     
```

## HTML and CSS Validation

The application automatically generates HTML files for validation purposes. Follow these steps to validate the HTML and CSS files:

1. **Run the Application**

   Follow the steps in the "Quick Start Guide" to launch the application.

2. **Generate HTML Files for Validation**

   The `app.py` code is set up to generate HTML files in the `html_generated_files_for_validation` directory each time a page is rendered. These files can be used for validation.

3. **Validate HTML and CSS**

   - Navigate to the `html_generated_files_for_validation` directory.
   - Use the following online tools to validate the generated HTML and CSS files:
     - HTML: [W3C Markup Validation Service](https://validator.w3.org/)
     - CSS: [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/)

   Upload the generated HTML files to these websites and review the validation results.

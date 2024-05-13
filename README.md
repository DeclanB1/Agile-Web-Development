# SportsSync Application

## Group Members

| Student Name   | Student Number | Github Username |
| -------------- | -------------- | --------------- |
| Lauren Hart    | 23164229       | lauhart         |
| Declan Barrett | 23074941       | DeclanB1        |
| Edward Le      | 23020568       | edwardisintou   |
| Matthew Chew   | 22974046       | mattcw9090      |

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

```bash
python3
import os
os.urandom(24)
```

c) Save generated secret key to variable SECRET_KEY in .env

4. **Navigate the Source Directory**

```bash
cd src
```

5. **Launch Application**

```bash
python3 app.py
```

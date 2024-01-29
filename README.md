<h1> RecipeApp API </h1>


This backend recipe API app was developed with **Django** and **PostgreSQL**, following Test-Driven Development (**TDD**) principles, and utilizes **Swagger** for clear documentation. **GitHub Actions** automates linting and unit tests, while **Docker/Docker Compose** simplifies deployment. Hosted on **AWS**, the app ensures scalability for efficient recipe management.




### **You can access the Recipe API website here** -> [**Link**](https://rebrand.ly/y2p7asp)


## Features

- Secure user authentication
- Easy creation of objects
- Simple filtering and sorting
- Effortless image uploading and viewing



## 🛠 Skills
Python, Django, PostgreSQL, TDD, GitHub Actions, Swagger, Docker/Docker Compose, AWS (EC2 & RDS).


## 🔗 Links
[![website](https://img.shields.io/badge/website-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://rebrand.ly/y2p7asp)

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yarin-getter/)




## Steps to get the project on your computer:

## <h3> Create a directory where you want to clone the project </h3>
`````shell script
mkdir recipe-project

`````

## Change into the directory
`````shell script
cd recipe-project
`````

## clone the project
`````shell script
git clone https://github.com/YarinDev/recipe-app-api
`````

**Build locally and run**

## Build the Docker image
`````shell script
docker-compose build
`````

## Start the development server
`````shell script
docker-compose run --rm app sh -c "python manage.py runserver"
`````

**Important:**

Adding the necessary packages to the requirements.txt or requirements.dev.txt(for dev-only packages) file is necessary before any push.
After the push, a series of checks are run automatically(see .github/worflows/checks.yml), including flake8 and the unit tests. Please make sure to format your code before pushing to the repository.
Flake8 which is a great toolkit for checking your code base against coding style (PEP8), and programming errors (like “library imported but unused” and “Undefined name”).

## Documentation
An auto API Documentation has been set using Swagger.
`````shell script
http://127.0.0.1:8000/api/docs/
`````
![recipe swagger](https://github.com/YarinDev/recipe-app-api/assets/74246091/e7a79f94-03da-4799-a144-96a2a90026aa)



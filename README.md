<div align="center">
  <h1> PalTech </h1>
</div>

## Idea:
This web application is specifically designed to assist store managers in efficiently managing multiple warehouses located in different cities and locations. Its primary purpose is to provide a streamlined solution for organizing products within these warehouses and effectively tracking the movement of each product. This includes monitoring the origin and destination of each product as it moves throughout the supply chain. By utilizing this application, store managers can optimize their inventory management processes, enhance operational efficiency, and maintain accurate records of product movement within their company's warehousing infrastructure.


## Functional Specifications:
- **Fully-Responsive:** The usage of bootstrap make it suitable for all screen sizes.
- **Login and Registration:** The application supports two types of authentication: worker and manager accounts.
  - Worker Account:
    - Limited access to website functionalities.
    - Can add new products to the system.
  - Manager Account:
    - Higher permissions and privileges.
    - Can add, delete, and modify various entities (locations, products, etc.).
    - Can observe the movements of all products.


## Programing Languages, Frameworks & Libraries Used:
- Pyhton 3.6.4
- Flask 2.0.3
- MySQL Workbench 8.0 CE
- Bootstrap 5.0.2


## Data Base:
-SQL Through MySQL Workbench.


## Getting Started:
"PrimeInventory" requires [Python](https://www.python.org/downloads/) to run.

1. **Clone the repository** to your local machine, open ur cmd & write down:
```sh
git clone <https://github.com/OsamaTbaileh/PrimeInventory>
```
2. **Activate your virtual environment**. If you don't have a virtual environment set up, create and activate one using the appropriate commands for your operating system.The following commands is to make new environment and to actiavte it:
```sh
Python -m venv                  ex: Python -m myEnv
call myEnv/Scripts/activate
```
3. **Install Flask and dependencies**:
Make sure your virtual environment is activated and in your cmd write down:
```sh
pip install Flask
```
4. **Navigate to the project directory** containing the Flask app's entry point file (`server.py`):
```sh
cd path/to/entry/PrimeInventory
```
5. **Start the server**:
```sh
python server.py
```
6. Open your web browser and visit the specified URL or endpoint to access the web app.(Usually it's localhost:5000):

```sh
localhost:5000
```



## Support

If you encounter any issues or have questions, please [submit an issue](https://github.com/your-username/your-repo/issues) or contact our support team at support@example.com.



## Some Screenshots of The Website:
## Home Page:
![Home Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/home_page.jpeg)


## Locations Page:
![Locations Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/locations_page.jpeg)


## Products & Movements Pages:
<p float="left">
  <img src="https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/products_page.jpeg" alt="Products Page Screenshot" width="45%" />
  <img src="https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/movements_page.jpeg" alt="Movements Page Screenshot" width="45%" />
</p>


## ERD:
![ERD Diagram](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/ERD_diagram.jpg)



### Note:
- login and registration will be added very soon, stay tuned.

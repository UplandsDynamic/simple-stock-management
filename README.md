# Simple Stock Management

This a simple stock management and inventory application. 

The app is designed to allow "stores" to request transfers of stock (or "order" it) from a central stock database (the "warehouse"). Warehouse stock is adjusted as stock transfers are ordered.

It has web frontend that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

## Key features

- Administrator may add, edit and delete stock from database.
- Store managers may request transfers ("order") stock from the "warehouse".
- Dynamic search of stock lines (SKU and description).
- Configurable pagination of results table.
- Transfer requests of stock lines are loaded to a "truck" (i.e. like "adding to a basket/cart" in an e-commerce system), before the request is submitted.
  - The "truck" retains the transfer data until the "Request truck dispatch" button is clicked. The truck data is retained across sessions (meaning the data remains in the truck even if the user logs out, then resumes their transfer at a later time).
  - Once the "Request truck dispatch" button is clicked, the transfer request process will complete. The truck empties and a single email containing a summary of the successful transfers - and any failures - is dispatched to both the requesting user and the warehouse administrator. Warehouse quantities are immediately adjusted accordingly.

## Key technologies

- Python 3.6
- Django
- Django-rest-framework
- Javascript (ReactJS)
- HTML5
- CSS3

## Screenshots

![Screenshot 1](./meta/img/screenshot_1.png?raw=true)
![Screenshot 2](./meta/img/screenshot_2.png?raw=true)
![Screenshot 4](./meta/img/screenshot_4.png?raw=true)

## Live Demo

There is a live demo available here:

https://sm.staging.aninstance.com

There are two test users - one for the warehouse administrator, the other for a 'store manager'. Credentials are:

Adminstrator:
Username: test_admin
Password: jduejHje(89K

Manager:
Username: test_manager
Password: jduejHje(89K

## Development Roadmap

- Addition of independent databases for each "store".

## Support

- Paid support services (including installation, configuration and development of bespoke features) are available. Please email productions@aninstance.com with "Simple Stock Management Support" in the subject field, or leave a message via the website form at: https://www.aninstance.com/contact

## Authors
- Dan Bright (Aninstance Consultancy), productions@aninstance.com

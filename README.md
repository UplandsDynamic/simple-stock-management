# Simple Stock Management

This a simple stock management and inventory application.

***Update: Version 4.x now released. The application now also includes unique stock records for every "store" and a "stock take" feature.***

The app is designed to allow "stores" to request transfers of stock ("order" it) from a central stock repository (the "warehouse"). Stock is adjusted for the "Warehouse Account" and the ordering "Store Account" as stock transfers are "ordered" and email notifications are sent to the "warehouse" administrator(s) and the ordering "store manager".

This application has web frontend that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

## Key features

- Administrator may add, edit and delete stock from database.
- Store managers may request transfers ("order") stock from the "warehouse".
- Dynamic search of stock lines (SKU and description).
- Configurable pagination of results table.
- Transfer requests of stock lines are loaded to a "truck" (i.e. like "adding to a basket/cart" in an e-commerce system), before the request is submitted.
  - The "truck" retains the transfer data until the "Request truck dispatch" button is clicked. The truck data is retained across sessions (meaning the data remains in the truck even if the user logs out, then resumes their transfer at a later time).
  - Once the "Request truck dispatch" button is clicked, the transfer request process will complete. The truck empties and a single email containing a summary of the successful transfers - and any failures - is dispatched to both the requesting user and the warehouse administrator. Warehouse quantities are immediately adjusted accordingly, both in the "Warehouse" and "Store" accounts.
- A "Stock take" feature compiles and emails detailed reports, consisting of:

  - For every unique stock line in a "Store Account" (see screenshot #10, below, for an example report):

    - SKU
    - Stock description
    - Units of opening stock
    - Units of closing stock
    - Change in stock units since last stock take
    - Number of units transferred since last stock take
    - Number of units recorded sold since last stock take
    - Number of units recorded as shrinkage since last stock take
    - Differential for units of unrecorded history since last stock take (i.e. unrecorded sales, unrecorded transfers, unrecorded loss)
    - Current transfer value of a unit
    - Current retail price of a unit
    - Total value of units recorded sold since last stock take
    - Total value of units recorded as shrinkage since last stock take
    - Total value of units transferred since last stock take
    - Total value differential of units with unrecorded history since last stock take, at present xfer price
    - Total value differential of units with unrecorded history since last stock take, at present retail price (i.e. unrecorded sales, unrecorded transfers, shrinkage)
    - Current total held stock transfer value at present xfer price
    - Current total held stock retail value at present retail price

  - Overview of the entire "Store Account" (see screenshot #10, below, for an example report):

    - Units of opening stock
    - Units of closing stock
    - Units of stock transferred since last stock take
    - Units of stock recorded sold since last stock take
    - Units of stock recorded as shrinkage since last stock take
    - Change in stock holding owing to unrecorded unit history since last stock take (i.e. unrecorded sales, unrecorded transfers, unrecorded loss)
    - Value of stock recorded sold since last stock take
    - Value of stock recorded as shrinkage since last stock take
    - Total value differential of units with unrecorded history since last stock take at current transfer value
    - Total value differential of units with unrecorded history since last stock take at current retail value (i.e. unrecorded sales, unrecorded transfers, unrecorded loss)
    - Total value of transfers since last stock take (at actual xfer prices)
    - All time total value of transfers (at actual xfer prices)
    - Value of held stock at current transfer price
    - Value of held stock at current retail price

- Automated removal of obsolete stock line records (lines with zero units of held stock) from the Store accounts following a successful stock take process
- Historical retention of previous stock take data (not currently exposed on the UI)

## Key technologies

Key technologies include: Python 3.7; Django; Django-rest-framework; Django_q (for asynchronous processes); Javascript (ReactJS); HTML5; CSS3; BootStrap 4.

## Live Demo

There is a live demo available here:

https://staging-ssm.aninstance.com

There are two test users - one for the warehouse administrator, the other for a 'store manager'. Credentials are:

Adminstrator:
Username: test_admin
Password: jduejHje(89K

Manager:
Username: test_manager
Password: jduejHje(89K

## Screenshots

![Screenshot 1](./meta/img/screenshot_1.png?raw=true)
![Screenshot 2](./meta/img/screenshot_2.png?raw=true)
![Screenshot 4](./meta/img/screenshot_4.png?raw=true)

![Screenshot 6](./meta/img/screenshot_6.png?raw=true)
![Screenshot 7](./meta/img/screenshot_7.png?raw=true)
![Screenshot 8](./meta/img/screenshot_8.png?raw=true)
![Screenshot 5](./meta/img/screenshot_5.png?raw=true)
![Screenshot 9](./meta/img/screenshot_9.png?raw=true)
![Screenshot 10](./meta/img/screenshot_10.png?raw=true)

## Docker deployment

The `master` branch of this repository is source for the dockerised version of the server. Please checkout the `frontend` branch for source of the dockerised frontend web client.

If deploying with Docker, it is highly recommended to use Docker Compose. Please find an example docker-compose file (which builds the entire stack, including the web client & server) in the `master` (server) branch.

The associated Docker images for server and client are available on DockerHub:

- Server:

  URL: <https://hub.docker.com/r/aninstance/simple-stock-management>

  To pull the image:

  `docker pull aninstance/simple-stock-management`

- Frontend client:

  URL: <https://hub.docker.com/r/aninstance/simple-stock-management-client>

  To pull the image:

  `docker pull aninstance/simple-stock-management`

To use this source code for non-dockerised builds, please amend the settings.py configuration file accordingly.

## Installation & usage (on Linux systems)

__These are basic instructions to install and run the app on an Linux Ubuntu 18.04 server, and for demonstration purposes only. They do not provide for a secure installation, such as would be required if the app was publicly available.__

__Steps should be taken to harden the environment if using in production, such as applying suitable file & directory permissions and ensuring both backend & frontend are served over a TLS connection.__

__A note on TLS: By default, `docker-compose-example.yml` exposes port to 80 on the server (`nginx`) container, and mounts the `settings.docker.insecure.py` Django settings fil to the `app` container, which serves the app over an unencrypted connection. To serve over TLS, change the exposed port to 443 and mount `settings.docker.py`__

### Brief installation instructions

To use the Docker images orchestrated with docker-compose:

- Create `ssm` directory, change to it and clone the repository:

  - `mkdir ssm`
  - `cd ssm`
  - `git clone https://github.com/Aninstance/simple-stock-management.git .`

- Create the following directories in the application's root directory. These are for persistent storage (i.e. they persist even after the app server & client containers have been stopped, started, deleted, upgraded):

  - `mkdir -p static postgres log/gunicorn`

- Set directory ownership. The default user and group as used in the demo are user: `ssm` (UID `9001`), group `ssm` (GID `9001`). These are the user and group both the server and app run under (they may be changed by editing the `Dockerfile`'s). To do this:

  - Create group: `sudo groupadd  -g 9001 ssm`
  - Add user to the host server: `sudo useradd --no-log-init -r -g 9001 -u 9001 ssm`
  - After ensuring you're still in the `ssm` directory, change ownership of directories and files: `sudo chown -R ssm:ssm static log config/secret_key`
  - Ensure the postgres database directories are owned by user UID 999: `sudo chown -R 999 postgres`

- Edit the following files to your specification:

  - `docker-compose-example.yml` - save as docker-compose.yml
  - `config/nginx/spm-example.config` - save as spm.conf
  - `config/.env.docker` - save as .env.docker (this is the frontend client configuration, where you may configure things like the number of items displayed per page)

  __Note: Don't forget to set the URL in both the `docker-compose.yml` (`app`'s `APP_URL` variable) and the `.env.docker` (`REACT_APP_API_ROUTE` & `REACT_APP_API_DATA_ROUTE` variables) files (as above).__

- You may remove the `src` directory, since the source will already be installed in the Docker image.

- Run this command to pull the Docker images and start the server (which serves both the server & frontend client components):

  `docker-compose up --build --force-recreate -d`

- If running for the first time (i.e. your persistent database folder is empty), define a superuser & by issuing the following commands:

  - Note down the name of the server app (exposing port 8000) that is output in the following command (e.g. `ssm_app_1`): `docker-compose ps`

  - Run the following, substituting `ssm_app_1` with the correct name for the server app, as discussed above.

    `docker exec -it ssm_app_1 python manage.py createsuperuser`

- If running for the first time, create an `administrators` group and add the new user to it, as follows:

  - Login at the django admin url - e.g. http://your_domain.tld/admin/
  - Click `add` next to `Groups` in the `Authentication & Authorization` section.
  - Name the new group `administrators`.
  - Under `Available permissions`, scroll to the bottom and select all the `spm_app` permissions, clicking the arrow on the right to add these to the `Chosen permissions` pane (you may hold `shift` to select multiple at once). Once done, click `Save`.
  - Navigate to `Home > Users > your username` and scroll down to the `Permissions` section. Select `administrators` from the `Available groups` box and double-click it. This moves it to `Chosen groups`. Scroll to the bottom of the page and click `Save`.
  - Click `LOG OUT` (top right)

- Navigate to the web client url - e.g. http://your_domain.tld __Note: When starting a newly built or pulled container for the first time, the web client may take several minutes (depending on your server's resources) to create a fresh build. You may get `This connection was reset` or timeout errors whilst the NPM build is occurring. Please be patient and try refreshing the page in a few moments.__

- Login to the web client using the superuser credentials you'd previously supplied. Begin using Simple Stock Management. 

### Brief UI instructions

Warehouse administrators:

- Plus sign button allows adding new stock lines
- Circular arrows button refreshes records from the database
- Pencil icon button in `Action` column allows editing of stock line
- Dustbin icon button in `Action` column allows deletion of a stock line

Store account managers:
  
- Head-&-shoulders icon (right of top header bar) switches between `Warehouse` account (from where transfers are requested) and the user's `Store` account
- Truck icon (right of top header bar) opens the user's "transfer truck"
- Circular arrows button refreshes records from the database
- Plus sign button allows manual addition of new lines to the `Store` account
- Pencil icon button in `Action` column allows editing of stock line data (e.g. change stock level, record a sale or shrinkage, etc)
- `New shrinkage` & `New recorded sold` update fields are ***disabled** during a stock line edit if the `stock quantity` field is changed. This is to prevent user error by inadvertent duplication of submitted data (i.e. user manually decrementing the `stock quantity` field whilst also recording the same data as `New recorded sold`). Likewise, the `stock quantity` field is disabled if the `New shrinkage` and/or `New recorded sold` fields are edited, for the same reason
- Eye icon button initiates a stock take

Note: The above guide is not definitive and is intended for users who know their way around Docker. Users would need to arrange database backups and to secure the application appropriately when used in a production environment.

## Development Roadmap

- Integration with the "ShopWired" e-commerce platform.

## Support

- Paid support services (including installation, configuration and development of bespoke features) are available. Please email productions@aninstance.com with "Simple Stock Management Support" in the subject field, or leave a message via the website form at: https://www.aninstance.com/contact

## Authors

- Dan Bright (Aninstance Consultancy), productions@aninstance.com

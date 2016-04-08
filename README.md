# Odoo Batch Export

## Purpose
A simple to use facility to export every field of every record from a model to a csv file

## Prerequisites
This module/readme was designed to be used in Odoo docker environments.

However - you can use it without - by simply creating the `/mnt/exports/` folder on your Odoo server

If you do not use docker - ignore the following prerequisites.

* Set up a volume in the `docker-compose.yml` file:
```bash
  volumes:
    - ./exports:/mnt/exports
```
* Create a `./exports` folder in the same folder as `docker-compose.yml`, and change the folder uid and gid to the Odoo uid/gid in the container (Run the snippet from outside the container):
```bash
$ mkdir exports
```
```bash
$ sudo chown `docker exec -i <container_name> bash -c "grep odoo /etc/passwd | cut -f3 -d:"`:`docker exec -i <container_name> bash -c "grep odoo /etc/passwd | cut -f4 -d:"` exports
```



* Add the following lines to your `Dockerfile`:
```bash
RUN mkdir -p /mnt/exports
```

## Usage
* Install the module, go to `Settings -> Batch Export -> Batch Export -> Create`
* Type a model name e.g `product.template` or `sale.order.line` - and give the record any name.
* Click the export button.
* Once complete - the csv file will be in your local exports folder (or /mnt/exports/ inside the container/server)

## Cron
* It's also possible to set up a cron job for the method call (example for product.template):
```xml
<record id='batch_export_product_cron' model='ir.cron'>
    <field name="name">Batch Product Export</field>
    <field name="active">1</field>
    <field name="user_id" ref="base.main_company"/>
    <field name="priority">5</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="model" eval="'batch.export'"/>
    <field name="function" eval="'cron_batch_export_model'"/>
    <field name="args" eval="('product.template',)"/>
</record>
```
* To change this to `sale.order` we would simply change the 'args' eval to `eval="('sale.order',)`, along with other relevant info such as name.


## Side Notes
* Exporting the res.users model will result in storing password hashes for all users in the .csv file. This is effectively the same as the information stored in the database.

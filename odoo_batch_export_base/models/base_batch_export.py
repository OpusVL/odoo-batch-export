# -*- coding: utf-8 -*-

##############################################################################
#
# odoo_batch_export_base
# Copyright (C) 2016 OpusVL (<http://opusvl.com/>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions
import time, tempfile, csv, codecs, cStringIO, shutil, gzip, os

# TODO Write to tempfile before end-product


class BatchExport(models.Model):
    _name = "batch.export"

    name = fields.Char(required=True)
    model = fields.Char(help="The technical model name i.e 'product.template'", required=True)
    use_compression = fields.Boolean(help="Will gzip the csv file after export.")

    @api.one
    def batch_export_model(self):
        try:
            ModelObj = self.env[self.model]
        except:
            raise exceptions.Warning("Model could not be found in the system!")
        self.generic_batch_export_model(ModelObj, self.model)

    @api.model
    def cron_batch_export_model(self, model):
        try:
            ModelObj = self.env[model]
        except:
            raise exceptions.Warning("Model could not be found in the system!")
        self.generic_batch_export_model(ModelObj, model)

    def generic_batch_export_model(self, ModelObj, model):
        fields = ModelObj.fields_get().keys()
        records = ModelObj.search([]).read(fields)
        file_prefix = '/mnt/exports/%s_export_' % model
        filename = file_prefix + time.strftime("%Y-%m-%d_%H:%M:%S") + '.csv'
        # Write directly to file
        with open(filename, 'w') as f:
            csv = UnicodeWriter(f)
            csv.writerow(fields)
            for record in records:
                row = [unicode(record[k]) for k in fields]
                csv.writerow(row)
        if self.use_compression:
            with open(filename, 'rb') as f_in, gzip.open(filename + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(filename)

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

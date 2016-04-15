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
from unicode_writer import UnicodeWriter
import time, shutil, gzip, os
# import tempfile

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
        self.generic_batch_export_model_filter(ModelObj, self.use_compression, self.model)

    @api.model
    def cron_batch_export_model(self, model, use_compression):
        try:
            ModelObj = self.env[model]
        except:
            raise exceptions.Warning("Model could not be found in the system!")
        self.generic_batch_export_model_filter(ModelObj, use_compression, model)

    def generic_batch_export_model_filter(self, ModelObj, use_compression, model):
        excluded_fields = []
        base_fields = ModelObj.fields_get().keys()
        new_fields = [field for field in base_fields if field not in excluded_fields]
        fields = new_fields if new_fields else base_fields
        records = ModelObj.search([]).read(fields)
        self.generic_batch_export_model(ModelObj, use_compression, model, records, fields)

    def generic_batch_export_model(self, ModelObj, use_compression, model, records, fields):
        file_prefix = '/mnt/exports/%s_export_' % model
        filename = file_prefix + time.strftime("%Y-%m-%d_%H:%M:%S") + '.csv'
        # Write directly to file
        with open(filename, 'w') as f:
            csv = UnicodeWriter(f)
            csv.writerow(fields)
            for record in records:
                row = [unicode(record[k]) for k in fields]
                csv.writerow(row)
        if use_compression:
            with open(filename, 'rb') as f_in, gzip.open(filename + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(filename)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

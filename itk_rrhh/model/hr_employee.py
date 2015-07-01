# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Humanytek. http://www.humanytek.com
#    soporte@humanytek.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _

class hr_employee_itk(osv.Model):

    _inherit = 'hr.employee'
    _description = 'Datos adicionales en Recursos Humanos para Interkey'
    _columns = {
        'bono': fields.related('user_id', 'bono', type='boolean', 
            relation='res.users', string='Bono'),
    }
    
hr_employee_itk()

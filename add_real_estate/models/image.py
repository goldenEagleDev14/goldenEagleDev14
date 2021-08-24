# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)
class ProductImages(models.Model):
    _name = 'biztech.product.images'
    _description = "Add Multiple Image in Product"

    
    name = fields.Char(string='Title', translate=True)
    alt = fields.Char(string='Alt', translate=True)
    attach_type = fields.Selection([('image', 'Image'),('video', 'Video')],
        default='image',
        string="Type")
    image = fields.Binary(string='Image')
    video_type = fields.Selection([('youtube', 'Youtube'),
                                   ('vimeo', 'Vimeo'),
                                   ('html5video','Html5 Video')],
        default='youtube',
        string="Video media player")
    cover_image = fields.Binary(string='Cover image',
        # required=True,
        help="Cover Image will be show untill video is loaded.")
    video_id = fields.Char(string='Video ID')
    video_ogv = fields.Char(string='Video OGV', help="Link for ogv format video")
    video_webm = fields.Char(string='Video WEBM', help="Link for webm format video")
    video_mp4 = fields.Char(string='Video MP4', help="Link for mp4 format video")
    sequence = fields.Integer(string='Sort Order')
    product_tmpl_id = fields.Many2one('product.product', string='Product')
    type_id = fields.Many2one('property.type', string='Unit Type')
    more_view_exclude = fields.Boolean(string="More View Exclude")



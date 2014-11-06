import os
import tempfile

import re

import bottle

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

formats = {
    'png': {
        'format': 'PNG',
        'mimetype': 'image/png'
    },
    'jpg': {
        'format': 'JPEG',
        'mimetype': 'image/jpeg'
    },
    'gif': {
        'format': 'GIF',
        'mimetype': 'image/gif'
    },
}

guides = {
    'qqvga': [160, 120],
    'hqvga': [240, 160],
    'qvga': [320, 240],
    'wqvga': [400, 240],
    'hvga': [480, 320],
    'vga': [640, 480],
    'wvga': [768, 480],
    'fwvga': [854, 480],
    'svga': [800, 600],
    'dvga': [960, 640],
    'wsvga': [1024, 600],
    'xga': [1024, 768],
    'wxga': [1366, 768],
    'fwxga': [1366, 768],
    'xga+': [1152, 864],
    'wxga+': [1440, 900],
    'sxga': [1280, 1024],
    'sxga+': [1400, 1050],
    'wsxga+': [1680, 1050],
    'uxga': [1600, 1200],
    'wuxga': [1920, 1200],
    '1080': [1920, 1080],
    '720': [1280, 720],
}

@bottle.route('/')
def index():
    return "it works!" 

@bottle.route('/<width>/<height>')
@bottle.route('/<width>/<height>/')
def image(width=320, height=240):

    width=int(width)
    height=int(height)
    
    format = bottle.request.query.get('f', 'png').lower()

    bg_color = bottle.request.query.get('bgcolor', 'aaaaaa').lower()
    fg_color = bottle.request.query.get('fgcolor', 'ffffff').lower()

    text = bottle.request.query.get('t', str(width) + 'x' + str(height)).lower()
    text_size = int(bottle.request.query.get('ts', 60))

    guide_list = [[int(y) for y in x.lower().split(',')] if ',' in x else x.lower() for x in bottle.request.query.getall('g')]
    guide_color = bottle.request.query.get('gcolor', fg_color).lower()

    try:
        if int(bg_color, 16):
            bg_color = '#' + bg_color
    except:
        pass

    try:
        if int(fg_color, 16):
            fg_color = '#' + fg_color
    except:
        pass

    try:
        if int(guide_color, 16):
            guide_color = '#' + guide_color
    except:
        pass

    if not format in formats:
        return bottle.HTTPError(code=404, output="That format is not supported")        

    image_file = tempfile.NamedTemporaryFile(suffix='.' + format, dir='/home/spencersr/holder.graphics/tmp/images/', delete=True)

    image = PIL.Image.new('RGB', size=(width, height), color=bg_color)

    draw = PIL.ImageDraw.Draw(image)

    print(text_size)

    font = PIL.ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf", text_size)
    guide_font = PIL.ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf", int(text_size/4.0))

    for guide in guide_list:
        guide_width, guide_height = guides.get(str(guide), guide)

        guide_offset_width = (width - guide_width) / 2.0
        guide_offset_height = (height - guide_height) / 2.0

        draw.rectangle(((guide_offset_width, guide_offset_height), (guide_offset_width + guide_width, guide_offset_height + guide_height)), fill=None, outline=guide_color)
        draw.text((guide_offset_width + 4, guide_offset_height + 4), str(guide_width) + 'x' + str(guide_height), fill=guide_color, font=guide_font)

    # Draw Center Text
    text_width, text_height = font.getsize(text)
    draw.text(((width - text_width) / 2.0, (height - text_height) / 2.0), text, fill=fg_color, font=font)

    image.save(image_file.file, formats[format]['format'])
    bottle.response.image_file = image_file

    return bottle.static_file(os.path.basename(image_file.name), root='/home/spencersr/holder.graphics/tmp/images/', mimetype=formats[format]['mimetype'])

def application(environ, start_response):
    app = bottle.default_app()
    return app.wsgi(environ, start_response) 

if __name__ == "__main__":
    bottle.debug(True)
    app = bottle.default_app()
    bottle.run(app, host='0.0.0.0', port='8685', reloader=True)


# Poseidon, extracts maps from neptun map image tiles
# http://neptun.unamur.be/items/browse?collection=30
import re, sys, os, requests, math
from PIL import Image

print("Poseidon Mosaic, glues together a matrix of map server tiles together.")

# Example tile url
# 'https://api.tiles.mapbox.com/v4/mapbox.streets/13/4235/2791.png?access_token=YOUR_TOKEN_KEY'
mapboxserv = ['https://api.tiles.mapbox.com/v4/', '.png?access_token=']
token = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'

# User provides zoom, lat/lng and number of x and y tiles

tileset_name = 'mapbox.streets'
base_path = './'

######################################################################
# Part 1 - Setup, read inputs
######################################################################
# read inputs either passed as argumenents or prompted

# Get arguments from command line or interactively
if len(sys.argv) == 8:
	zoom, lat, lng, width, height, token, tileset_name = sys.argv[1:9]
elif len(sys.argv) == 1:
    try:
        zoom = raw_input("Zoom level (1 is world scale): ")
        lat = raw_input("Latitude: ")
        lng = raw_input("Longitude: ")
        width = raw_input("Total tiles width: ")
        height = raw_input("Total tiles height: ")
    except NameError:
        print("Hmmm you are using Python 3.x perhaps...")
        zoom = input("Zoom level (1 is world scale): ")
        lat = input("Latitude: ")
        lng = input("Longitude: ")
        width = input("Total tiles width: ")
        height = input("Total tiles height: ")
else:
    exit("Command format:\npython posmos.py zoom lat lng tiles_width tiles_height token tileset")

# convert var formats
zoom = int(zoom)
lat = float(lat)
lng = float(lng)
width = int(width)
height = int(height)

# Converting from lat/lng to tile index
ntiles = math.pow(2, zoom)
xloc = int(ntiles * ((lng + 180) / 360))
yloc = int(ntiles * (1 - (math.log(math.tan(lat/180*math.pi) + 1/math.cos(lat/180*math.pi)) / math.pi)) / 2)

# make directory to hold tiles and result
tiles_path = base_path + '/tiles'
try:
	os.makedirs(tiles_path + '/zoom_' + str(zoom))
except:
	print("Folder already exists, this may overwrite data.")

######################################################################
# Part 2 - retrieve tiles
######################################################################

# go through columns
x = 0
while x < width:
    y = 0
    # go through rows, down column
    while y < height:
        print(str(x) + ',' + str(y))
        
        # check if file exists locally
        if not os.path.exists(tiles_path + '/' + tileset_name + '_' + str(zoom) + '-' + str(x + xloc) + '-' + str(y + yloc) + '.png'):
            # check if it is available online
            try:
                # get the image
                res = requests.get(mapboxserv[0] + tileset_name + '/' + str(zoom) + '/' + str(x + xloc) + '/' + str(y + yloc) + mapboxserv[1] + token)
                res.raise_for_status()
            except requests.exceptions.HTTPError:
                print("Failed to find a required tile image!")
    
            # file exists, we download it -> res
            f = open(tiles_path + '/zoom_' + str(zoom) + '/' + tileset_name + '_' + str(zoom) + '-' + str(x + xloc) + '-' + str(y + yloc) + '.png', 'wb')
            f.write(res.content)
            f.close()
    
        # increment y
        y = y + 1

    # increment x
    x = x + 1

######################################################################
# Part 3 - combine tiles to make an image
######################################################################

# output file
outputfolder = base_path + '/outputs'
try:
	os.makedirs(outputfolder)
except:
	print("Output folder already exists, this may overwrite data.")

# determine the tile sizes by looking at the origin/first tile
tile = Image.open(tiles_path + '/zoom_' + str(zoom) + '/' + tileset_name + '_' + str(zoom) + '-' + str(xloc) + '-' + str(yloc) + '.png')
size = tile.size[0] # assumes tile is square!

# create blank image
mosaic = Image.new("RGB", (width * size, height * size))

# determine number of tiles in x,y dimension
x = 0
while x < width:
    y = 0
    # go through rows, down column
    while y < height:
        tile = Image.open(tiles_path + '/zoom_' + str(zoom) + '/' + tileset_name + '_' + str(zoom) + '-' + str(x + xloc) + '-' + str(y + yloc) + '.png')
        mosaic.paste(tile, (x * size, y * size))

        y = y + 1
    x = x + 1

# Save final image
mosaic.save(outputfolder + '/' + tileset_name + '_zoom-' + str(zoom) + '_lat-' + str(lat) + '_lng-' + str(lng) + '_width-' + str(width) + '_height-' + str(height) + '.png')

POLYGONS_BASE_URL = "http://firmware.freifunk-muensterland.de/md-fw-dl/shapes"
-- WIFI_SCAN_COMMAND = 'iwinfo client0 scan'
WIFI_SCAN_COMMAND = 'iwlist wlan0 scan'

domains = { count = 0 }
wifis = {}
JSON = (loadfile "JSON.lua")()

function find_all_polygons()
	local file = assert(io.popen('wget -qO - ' .. POLYGONS_BASE_URL, 'r'))
	for line in file:lines() do
		if ( string.match(line, "geojson") and not string.match(line, "highres")) then
			line = string.gsub(line, "^.->", "", 1)
			line = string.gsub(line, "<.*", "", 1)
			domains["count"] = domains["count"] + 1
			domains[domains["count"]] = line
		end
	end
end
function report_polygon_match(count)
	print("Dieser Knoten liegt im Polygon" .. domains[count] ..".")
end
function read_whole_file(file)
        local content = file:read("*all")
	file:close()
        return content
end
function test_polygon_contains_point(own_coordinates, polygon)
	c = false
	j = #polygon
	for i=1,#polygon,1 do
		if (not ( polygon[i][2] > own_coordinates[2] ) == ( polygon[j][2] > own_coordinates[2] )) and ( own_coordinates[1] < ( polygon[j][1] - polygon[i][1] ) * ( own_coordinates[2] - polygon[i][2] ) / ( polygon[j][2] - polygon[i][2] ) + polygon[i][1] ) then
			c = not c
		end
		j=i
	end
	print(c)
	return c
end
function test_all_polygons()
	for i = 2, domains["count"] do
		local file = assert(io.popen('wget -qO - ' .. POLYGONS_BASE_URL .. '/' .. domains[i], 'r'))
		local polygon_json = read_whole_file(file)
		local polygon = JSON:decode(polygon_json)['features'][1]['geometry']['coordinates'][1]
		test_polygon_contains_point({ 7.542114,51.947651}, polygon)
	end

end
function parse_wifis()
	local file = assert(io.popen(WIFI_SCAN_COMMAND))
	local counter = 0;
	for line in file:lines() do
		if line:find('Address') ~= nil then
			counter = counter + 1
			wifis[counter] = {}
			wifis[counter]["macAddress"] = line:gsub ('.*(%w%w:%w%w:%w%w:%w%w:%w%w:%w%w).*', '%1')
		elseif line:find('hannel') ~= nil then
			wifis[counter]["channel"] = line:match('%d+')
		elseif line:find('Signal') ~= nil then
			wifis[counter]["signalStrength"] = line:gsub( '.+Signal.+%-(%d%d).*', '%-%1')
		end
	end
end
function get_coordinates()
	post = {}
	post["wifiAccessPoints"] = wifis
	poststring = JSON:encode(post)
	local http = require("socket.http")
	local ltn12 = require("ltn12")

	local path = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyA4-TkuE0b2XJC0s4z2TyObyTNHtQgb9Wg"
	local response_body = { }
	local res, code, response_headers, status = http.request {
		url = path,
		method = "POST",
		headers = {
			["Content-Type"] = "application/json",
			["Content-Length"] = poststring:len()
		},
		source = ltn12.source.string(poststring),
		sink = ltn12.sink.table(response_body)
	}
	luup.task('Response: = ' .. table.concat(response_body) .. ' code = ' .. code .. '   status = ' .. status,1,'Sample POST request with JSON data',-1)
end

-- find_all_polygons()
-- test_all_polygons()
parse_wifis()
get_coordinates()

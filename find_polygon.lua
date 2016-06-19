POLYGONS_BASE_URL = "http://firmware.freifunk-muensterland.de/md-fw-dl/shapes"
domains = { count = 0 }

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
	local f = io.open(file, "rb")
        local content = f:read("*all")
	f:close()
        return content
end
-- function test_polygon_contains_point(number_points, 
function test_all_polygons()
	local inspect = require('inspect')
	for i = 1, domains["count"] do
		local file = assert(io.popen('wget -qO - ' .. POLYGONS_BASE_URL .. '/' .. domains[i], 'r'))
		local polygon_json = read_whole_file(file)
		local polygon = JSON:decode(polygon_json)
		print(inspect(polygon))

	end

end

find_all_polygons()
test_all_polygons()

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
		os.exit()

	end

end

find_all_polygons()
test_all_polygons()
-- test_polygon_contains_point({ -1, 0.25 }, {{0,0},{0,1},{1,0}})
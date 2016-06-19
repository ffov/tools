POLYGONS_BASE_URL = "http://firmware.freifunk-muensterland.de/md-fw-dl/shapes"
domains = { count = 0 }

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
function test_all_polygons()
	for i = 1; i <= domains["count"], i = i+1 do
	end

end

find_all_polygons()
test_all_polygons()

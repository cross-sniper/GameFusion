function setup()
	x = 30
	y = 30
	hp = 10
end

function draw()
	--fillRect(x,y,30,30,"red")
	for i=1, hp do
		draw_sprite("sprites/heart.png", 20 * i,30)
	end
	draw_sprite("sprites/icon.png", x,y)
end

function update(dt)
	if(keyDown("a")) then
		x = x - 200 * dt
	elseif(keyDown("d")) then
		x = x + 200 * dt
	end

	if(keyDown("w")) then
		y = y - 200 * dt
	elseif(keyDown("s")) then
		y = y + 200 * dt
	end

	if keyPressed("f") then hp = hp - 1 end

end
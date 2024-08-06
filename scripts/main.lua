-- GameFusion is somewhat like microstudio, but you can use whatever editor and sprite software you like
-- it's also made entirely in python, and uses lua for game
-- it's in early development stages, but we're getting there
function setup()
	x = 30
	y = 30
	score = 0
end

function draw()
	--fillRect(x,y,30,30,"red")
	drawSprite("sprites/icon.png", x,y,32,32)
	drawText("score: "..score, 20,20,20,"white")

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


end
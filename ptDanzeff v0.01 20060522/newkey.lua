-- ptDanzeff LuaNewkey v0.01 (20060522) by LilCthulhu
-- http://www.palmtime.com/ - lilcthulhu@palmtime.com

-- Please read readme.txt and license.txt

-- ptDanzeff LuaOSK: Include ptDanzeff LuaOSK.
dofile(".\\danzeff\\danzeff.lua")

-- ptDanzeff LuaOSK requires that screen variable is set to screen
-- screen = screen -- not required for lua adaptation
bg = Image.load("bg.png")
white = Color.new(255,255,255)
val = ""

function danzeff_demo()
	-- ptDanzeff LuaOSK: Initialise and load OSK graphics
	danzeff_load()

	-- ptDanzeff LuaOSK: Returns whether OSK is initialised or not as a boolean
	if (not danzeff_isinitialized()) then 
		return 
	end

	-- ptDanzeff LuaOSK: Position OSK on screen
	danzeff_moveTo(220,20)
		
	while true do
		-- Prepare background
		screen:blit(0, 0, bg, 0, 0, bg:width(), bg:height(), false)
		
		-- ptDanzeff LuaOSK: Render OSK on screen
		danzeff_render() 	

		-- ptDanzeff LuaOSK: Returns OSK input as an integer
		cha = danzeff_readInput(Controls.read())
	
		-- Now Evaluate return value and take proper action
		if (cha ~= 0 and cha ~= 1 and cha ~= 2) then
			if (cha == 8 or cha == string.byte("\010")) then 
				val = string.sub(val,1,(string.len(val)-1)) 
			elseif (cha == 13) then 
				val = ""
			elseif (cha == 4) then
				return 
			else 
				val = val .. string.char(cha)
			end
		end

		-- Print current input string
		screen:print(5, 233, val, white)
		
		-- Refresh screen
		screen.flip()	
	end
end

-- Launch ptDanzeff LuaOSK Demo
danzeff_demo()

-- ptDanzeff LuaOSK: Release OSK graphics memory
danzeff_free()
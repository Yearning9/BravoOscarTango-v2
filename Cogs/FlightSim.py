import datetime
import os
import discord
import requests
from PIL import Image, ImageDraw, ImageFont
from discord import app_commands
from discord.ext import commands

avail_checklists = []
for checklists in os.listdir('./Utils/Checklists'):
    if checklists.endswith('.pdf'):
        avail_checklists.append(checklists[:-4])

with open('Private/WxAPI.txt', 'r') as x:
    xapi: str = x.read()
hdr = {"X-API-Key": xapi}

with open('Private/FPD.com API.txt', 'r') as q:
    fpd_api: str = q.read()

with open('Private/mapbox.txt', 'r') as z:
    mb_api: str = z.read()

fltplan_id = 0

correct_sim_types = ['xplane11', 'xplane', 'fsx', 'fs9', 'pmdg', 'pdf']


class FlightSim(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name='metar', description='Returns METAR for a given airport ICAO')
    @commands.cooldown(1, 3)
    @app_commands.describe(icao='Required airport ICAO code')
    async def metar(self, ctx, icao: str):

        if len(icao) != 4:
            await ctx.reply("ICAO code must be composed of 4 characters", mention_author=False)
            return
        try:
            req = requests.get('https://api.checkwx.com/metar/{}/decoded'.format(icao), headers=hdr, timeout=5)
        except requests.exceptions.ConnectTimeout:
            return await ctx.reply(
                "Timeout error while requesting METAR, API servers are probably offline. You can report this issue on the support server (/support), or try again later",
                mention_author=False)
        except Exception as err:
            return await ctx.reply(
                f"Error while requesting METAR, please report this issue on the support server (/support):\n`{err}`",
                mention_author=False)

        if req.status_code != 200:
            return await ctx.reply(
                f"Error {req.status_code} while retrieving info for {icao.upper()}, either the website is down or the airport you chose is not available",
                mention_author=False)
        else:

            await ctx.defer()

            resp = req.json()

            if resp["results"] == 0:
                return await ctx.send("No results, please check for typos or try a different ICAO")

            # with open('./Utils/wx.json', 'w') as f:
            #     json.dump(resp, f, indent=4)

            layerint = len(resp["data"][0]["clouds"])  # integer for number of cloud layers

            wxint = 0
            if "conditions" in resp["data"][0]:
                wxint = len(resp["data"][0]["conditions"])  # presence of wx conditions

            visbool = "visibility" in resp["data"][0]  # presence of vis data

            if 'wind' in resp['data'][0]:
                gustbool = "gust_kts" in resp["data"][0]["wind"]  # presence of gusts
                wind_bool = True
            else:
                gustbool = False
                wind_bool = False

            name = resp["data"][0]["station"]["name"]
            degrees = 0
            speed = 0
            if wind_bool:
                degrees = resp["data"][0]["wind"]["degrees"]
                speed = resp["data"][0]["wind"]["speed_kts"]
            temp = resp["data"][0]["temperature"]["celsius"]
            dew = resp["data"][0]["dewpoint"]["celsius"]
            humidity = resp["data"][0]["humidity"]["percent"]
            inhg = resp["data"][0]["barometer"]["hg"]
            hpa = resp["data"][0]["barometer"]["hpa"]
            obs = resp["data"][0]["observed"]
            cond = resp["data"][0]["flight_category"]
            raw = resp["data"][0]["raw_text"]

            # points = []

            lat: float = resp["data"][0]["station"]["geometry"]["coordinates"][1]
            long: float = resp["data"][0]["station"]["geometry"]["coordinates"][0]

            # KEEP THIS IN CASE MAPBOX NEEDS TO BE REPLACED

            # points.append(tuple([lat, long]))
            #
            # marker_outline = CircleMarker((long, lat), 'white', 18)
            # marker = CircleMarker((long, lat), '#0036FF', 12)
            # icon_flag = IconMarker((long + 0.008, lat), './Utils/icon-flag.png', 12, 32)
            #
            # m = StaticMap(700, 300, 10, 10)
            # m.add_marker(marker_outline)
            # m.add_marker(marker)
            # m.add_marker(icon_flag)
            #
            # image = m.render(zoom=8)
            # image.save('Utils/metar.png')

            tile = requests.get(
                f"https://api.mapbox.com/styles/v1/yearning9/cl3t8si9n009k15msqlz5wvx6/static/{long},{lat},13,0/700x512?access_token={mb_api}")

            ftile = open('Utils/metar.png', 'wb')
            ftile.write(tile.content)
            ftile.close()

            file = discord.File('Utils/metar.png')

            metar = discord.Embed(
                title="Requested METAR for {} - {}".format(icao.upper(), name),
                description="Raw: {}".format(raw),
                colour=discord.Colour.from_rgb(97, 0, 215)
            )
            if wind_bool:
                if not gustbool:
                    metar.add_field(name="Wind:", value="{}° at {} kts".format(degrees, speed))
                else:
                    gust: int = resp["data"][0]["wind"]["gust_kts"]
                    metar.add_field(name="Wind:", value="{}° at {} kts, gusts {} kts".format(degrees, speed, int(gust)))
            else:
                metar.add_field(name="Wind:", value="Calm")

            metar.add_field(name="Temp/Dewpoint:", value="{}°C/ {}°C".format(temp, dew))
            metar.add_field(name="Altimeter:", value="{} hPa/ {} inHg".format(hpa, inhg))
            if visbool:
                vismil = resp["data"][0]["visibility"]["miles"]
                vismet = resp["data"][0]["visibility"]["meters"]
                metar.add_field(name="Visibility:", value="{} meters/ {} miles".format(vismet, vismil))

            metar.add_field(name="Humidity:", value="{}%".format(humidity))
            metar.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif")
            metar.set_footer(text="Observed at {}. Flight category: {}".format(obs, cond))
            if wxint > 0:
                weather = resp["data"][0]["conditions"][0]["text"]
                metar.add_field(name="Weather condition:", value="{}".format(weather))

            if layerint == 1:
                clouds = resp["data"][0]["clouds"][0]["text"]
                if 'feet' in resp["data"][0]["clouds"][0]:
                    clofeet = resp["data"][0]["clouds"][0]["feet"]
                    metar.add_field(name="Cloud condition:", value="{}ft {}".format(clofeet, clouds))
                else:
                    metar.add_field(name="Cloud condition:", value="{}".format(clouds))
            elif layerint == 2:
                clouds = resp["data"][0]["clouds"][0]["text"]
                clofeet = resp["data"][0]["clouds"][0]["feet"]
                clouds1 = resp["data"][0]["clouds"][1]["text"]
                clofeet1 = resp["data"][0]["clouds"][1]["feet"]
                metar.add_field(name="Cloud condition:",
                                value="{}ft {}/ {}ft {}".format(clofeet, clouds, clofeet1, clouds1))
            elif layerint == 3:
                clouds = resp["data"][0]["clouds"][0]["text"]
                clofeet = resp["data"][0]["clouds"][0]["feet"]
                clouds1 = resp["data"][0]["clouds"][1]["text"]
                clofeet1 = resp["data"][0]["clouds"][1]["feet"]
                clouds2 = resp["data"][0]["clouds"][2]["text"]
                clofeet2 = resp["data"][0]["clouds"][2]["feet"]
                metar.add_field(name="Cloud condition:",
                                value="{}ft {}/ {}ft {}/ {}ft {}".format(clofeet, clouds, clofeet1, clouds1, clofeet2,
                                                                         clouds2))
            else:
                metar.add_field(name="Cloud condition:", value="Not Specified / Cloud data error")

            metar.set_image(url='attachment://metar.png')

            await ctx.send(embed=metar, file=file)

    @commands.hybrid_command(name='charts', description='Returns PDF chart for a given airport ICAO')
    @app_commands.describe(icao='Required airport ICAO code')
    async def charts(self, ctx, icao: str):

        if len(icao) != 4:
            return await ctx.reply("ICAO code must be 4 characters long", mention_author=False)

        url = f"http://www.uvairlines.com/admin/resources/{icao.upper()}.pdf"

        await ctx.defer()

        try:
            request = requests.get(url, headers=hdr, timeout=5)
        except requests.exceptions.ConnectTimeout:
            return await ctx.reply(
                "Timeout error while requesting charts. You can report this issue on the support server (/support), or try again later",
                mention_author=False)
        except Exception as err:
            return await ctx.reply(
                f"Error while requesting charts, website is probably offline. You can report this issue on the support server (/support):\n`{err}`",
                mention_author=False)

        if request.status_code != 200:
            await ctx.reply(
                f"Error {request.status_code} while retrieving charts for {icao.upper()}, either the website is down or the airport you chose is not available",
                mention_author=False)
        else:

            charts = discord.Embed(
                title=f"Requested charts for {icao.upper()}",
                description=f"Download or view the charts at: [Link]({url})",
                colour=discord.Colour.from_rgb(97, 0, 215)
            )
            charts.set_footer(
                text=f"You can also check the METAR for this airport with `/metar {icao.upper()}`")
            charts.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif")
            await ctx.reply(embed=charts, mention_author=False)
            return

    @commands.hybrid_command(name='checklist',
                             description='Returns checklist for supported aircraft, leave blank for list')
    @app_commands.describe(plane='Aircraft ICAO code')
    async def checklist(self, ctx, plane: str = 'avail'):

        if plane == 'avail':
            avplanes = ', '.join(avail_checklists)
            return await ctx.reply(f'Checklists are currenly available for these planes: **{avplanes}**',
                                   mention_author=False)

        elif len(plane) != 4:
            return await ctx.reply(
                f"You must input a correct 4 character ICAO code for your plane, check available checklists with /checklist",
                mention_author=False)
        elif plane.upper() in avail_checklists:
            clfile = discord.File(f'./Utils/Checklists/{plane.upper()}.pdf')
            return await ctx.reply(f"Here's your requested checklist for the {plane.upper()}:", file=clfile,
                                   mention_author=False)
        else:
            return await ctx.reply(
                f"Unfortunately the checklist you requested is not available, check a list of available checklists with /checklist",
                mention_author=False)

    @commands.hybrid_command(name='flightplan', description='Calculates a flight plan between two given airports')
    @commands.cooldown(1, 10)
    @app_commands.describe(dep='Departure airport ICAO code', arr='Arrival airport ICAO code')
    async def flightplan(self, ctx, dep: str, arr: str):

        if len(dep) != 4 or len(arr) != 4:
            await ctx.send('You need to specify two valid airport ICAO codes to create a flight plan')
            self.flightplan.reset_cooldown(ctx)
            return

        await ctx.defer()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + fpd_api
        }
        data = '{"fromICAO":"immensecock","toICAO":"giganticpenis"}'
        data = data.replace("immensecock", dep)
        data = data.replace("giganticpenis", arr)

        try:
            response = requests.post('https://api.flightplandatabase.com/auto/generate', headers=headers, data=data)
        except Exception as err:
            return await ctx.reply(
                f"Error while requesting flight plan, API servers are probably offline. You can report this error on the support server (/support):\n`{err}`",
                mention_author=False)

        if response.status_code != 201:
            await ctx.send(
                f"Error {response.status_code} while generating the flight plan, try with different ICAO codes\n```{response.json()['errors'][0]['message']}```")
            self.flightplan.reset_cooldown(ctx)
            return

        plan = (str(response.json()))[7:14]

        retrieve = requests.get(f'https://api.flightplandatabase.com/plan/{plan}')
        if retrieve.status_code != 200:
            await ctx.send(
                f'There was an error while processing the flight plan: **{retrieve.status_code}**, try with different ICAO codes')
            self.flightplan.reset_cooldown(ctx)
            return

        flp = retrieve.json()
        flpid = flp['id']
        dep_icao = flp['fromICAO']
        arr_icao = flp['toICAO']
        dep_name = flp['fromName']
        arr_name = flp['toName']
        dist = int(flp['distance'])
        cr_alt = flp['maxAltitude']
        wpt_num = flp['waypoints']  # important
        link = f'https://flightplandatabase.com/plan/{flpid}'
        airac = flp['cycle']['ident']

        global fltplan_id

        fltplan_id = flpid

        i = 1
        route = f'***{dep_icao}***'
        route += ' ' + '[SID]'

        while i <= wpt_num:

            if flp['route']['nodes'][i]['ident'] != f'{arr_icao}':

                if flp['route']['nodes'][i]['ident'] == flp['route']['nodes'][i + 1]['ident']:
                    i += 1
                    continue
                elif flp['route']['nodes'][i]['via'] is None:
                    del flp['route']['nodes'][i]['via']
                    flp['route']['nodes'][i]['via'] = {}
                    flp['route']['nodes'][i]['via']['ident'] = 'None'
                    if i != 1:
                        if flp['route']['nodes'][i - 1]['via']['ident'] == 'None':
                            route += f" **DCT** {flp['route']['nodes'][i]['ident']}"
                        else:
                            route += f" {flp['route']['nodes'][i - 1]['ident']} **DCT** " + \
                                     flp['route']['nodes'][i]['ident']
                    else:
                        route += f" {flp['route']['nodes'][i]['ident']}"
                    i += 1
                    continue
                elif flp['route']['nodes'][i]['via']['ident'] != flp['route']['nodes'][i - 1]['via']['ident']:
                    if flp['route']['nodes'][i - 1]['via']['ident'] == 'None':
                        route += ' ' + '**DCT**' + ' ' + flp['route']['nodes'][i]['ident'] + ' ' + '**' + \
                                 flp['route']['nodes'][i]['via']['ident'] + '**'
                    else:
                        route += ' ' + flp['route']['nodes'][i]['ident'] + ' ' + '**' + flp['route']['nodes'][i]['via'][
                            'ident'] + '**'
                    i += 1
                    continue
                else:
                    i += 1
            else:
                route += ' ' + flp['route']['nodes'][i - 1]['ident'] + ' ' + '[STAR]' + ' '
                route += f'***{arr_icao}***'
                break

        base_url = 'https://www.flightplandatabase.com/plan/{fltplan_id}/download/'

        flp_embed = discord.Embed(
            title=f"Here's your flight plan: **{dep_icao} → {arr_icao}**",
            description=f"Flight plan: {route}",
            colour=discord.Colour.from_rgb(97, 0, 215)
        )
        flp_embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
        flp_embed.add_field(name='Departure Airport:', value=dep_name)
        flp_embed.add_field(name='Arrival Airport:', value=arr_name)
        flp_embed.add_field(name='Distance / Cruise Altitude:', value=f'{dist}nm/{cr_alt}ft')
        flp_embed.add_field(name='Downloads:',
                            value=f'[X-PLane 11]({base_url}xplane11) | [X-Plane 10/9]({base_url}xplane) | [FSX]({base_url}fsx) | [FS9]({base_url}fs9) | [PMDG]({base_url}pmdg) | [PDF]({base_url}pdf)')
        flp_embed.add_field(name='Link to full flight plan:', value=link)
        flp_embed.set_footer(
            text=f'Using data from the Flight Plan Database (https://flightplandatabase.com), AIRAC Cycle: {airac[3:]}')

        await ctx.reply(embed=flp_embed, mention_author=False)

    @commands.hybrid_command(name='info', description='Returns information for a given airport ICAO')
    @app_commands.describe(icao='Required airport ICAO code')
    async def info(self, ctx, icao: str):

        if len(icao) != 4:
            await ctx.reply("Please input a correct ICAO code", mention_author=False)
            return

        await ctx.defer()

        try:
            request = requests.get(f'https://api.flightplandatabase.com/nav/airport/{icao.upper()}')
        except Exception as err:
            return await ctx.reply(
                f"Error while requesting info, API servers are probably offline. You can report this issue on the support server (/support) or try again later:\n`{err}`",
                mention_author=False)

        if request.status_code != 200:
            return await ctx.reply(
                f"Error {request.status_code} while retrieving info for {icao.upper()}, either the website is down or the airport you chose is not available\n```{request.json()['message']}```",
                mention_author=False)

        else:
            info = request.json()
            # with open('./Utils/info.json', 'w') as f:
            #     json.dump(info, f, indent=4)

            json_icao = info['ICAO']
            iata = info['IATA']
            name = info['name']
            lat: float = info["lat"]
            lon: float = info["lon"]
            runway_int = info['runwayCount']
            elevation = int(info['elevation'])
            mag_var = round(info['magneticVariation'], 2)
            timezone = info['timezone']['name']
            metar = info['weather']['METAR']
            taf = info['weather']['TAF']

            if info['timezone']['offset'] is not None:

                notime = False

                offset1 = info['timezone']['offset'] / 3600

                if offset1 == 1:
                    offset1 = 0.0

                offset = str(offset1)
                offset = offset.replace('.', ':')
                offset += '0'
                if -10 < offset1 < 10:
                    if '-' not in offset:
                        offset = '+0' + offset
                    else:
                        offset = list(offset)
                        del offset[0]
                        offset = "".join(offset)
                        offset = '-0' + offset
                if '-' not in offset and '+' not in offset:
                    offset = '+' + offset
                offset = list(offset)
                if len(offset) == 7:
                    del offset[6]
                if offset[4] != 0:
                    if offset[4] == '5':
                        offset[4] = '3'
                    elif offset[4] == '7':
                        offset[4] = '4'
                offset = "".join(offset)

                epoch = datetime.datetime.utcnow().timestamp()
                if info['timezone']['offset'] != 3600:
                    local = epoch + info['timezone']['offset']
                else:
                    local = epoch
                utc = datetime.datetime.fromtimestamp(epoch).strftime('%d-%m-%Y %H:%M:%S')
                local = datetime.datetime.fromtimestamp(local).strftime('%d-%m-%Y %H:%M:%S')

            else:
                notime = True
                offset, timezone, local = "N/A"
                epoch = datetime.datetime.utcnow().timestamp()
                utc = datetime.datetime.fromtimestamp(epoch).strftime('%d-%m-%Y %H:%M:%S')

            # marker_outline = CircleMarker((lon, lat), 'white', 18)
            # marker = CircleMarker((lon, lat), '#0036FF', 12)
            # m = StaticMap(500, 300, 10, 10, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
            # m.add_marker(marker_outline)
            # m.add_marker(marker)
            #
            # image = m.render(zoom=8)
            # image.save('Utils/info.png')

            tile = requests.get(
                f"https://api.mapbox.com/styles/v1/yearning9/cl3t8si9n009k15msqlz5wvx6/static/{lon},{lat},13,0/700x512?access_token={mb_api}")

            ftile = open('Utils/info.png', 'wb')
            ftile.write(tile.content)
            ftile.close()

            info_embed = discord.Embed(
                title=f'{json_icao} - {iata}',
                description=name,
                colour=discord.Colour.from_rgb(97, 0, 215)
            )

            runways = ''

            i = 0
            # j = 0

            if runway_int == 1:
                runways += f"{info['runways'][i]['ends'][0]['ident']} / {info['runways'][i]['ends'][1]['ident']}"
                len_width = f"{int(info['runways'][0]['length'])}ft x {int(info['runways'][0]['width'])}ft"
                hdg = int(info['runways'][0]['bearing'])
                if hdg + 180 > 360:
                    rwy_hdg = f'{hdg} - {hdg - 180}'
                else:
                    rwy_hdg = f'{hdg}°/{hdg + 180}°'
                info_embed.add_field(name='Runways:', value=runways)
                info_embed.add_field(name='Airport Elevation:', value=f'{str(elevation)}ft')
                info_embed.add_field(name='Magnetic Variation:', value=f'{str(mag_var)}°')
                if notime:
                    info_embed.add_field(name='Timezone:', value='N/A')
                else:
                    info_embed.add_field(name='Timezone:', value=f'{offset} UTC, {timezone}')
                # for ils in info['runways'][i]['navaids']:
                #     if ils == "LOC-ILS":
                #         print(info['runways'][i]['navaids'][j]['name'])
                #         break
                #     else:
                #         j += 1
                img = Image.open('Utils/info.png')
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype('./Utils/font.ttf', 25)
                draw.text((0, 460), f'{runways} - {len_width} - {rwy_hdg}', fill=(0, 0, 0), font=font,
                          stroke_width=3, stroke_fill=(255, 255, 255))
                img.save('Utils/info_done.png')
            else:
                img = Image.open('Utils/info.png')
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype('./Utils/font.ttf', 20)
                while i < runway_int:
                    px = 460 - i * 19
                    curr_rwy = f"{info['runways'][i]['ends'][0]['ident']} / {info['runways'][i]['ends'][1]['ident']}"
                    runways += f"{info['runways'][i]['ends'][0]['ident']} / {info['runways'][i]['ends'][1]['ident']} - "
                    len_width = f"{int(info['runways'][i]['length'])}ft x {int(info['runways'][i]['width'])}ft"
                    hdg = int(info['runways'][i]['bearing'])
                    if hdg + 180 > 360:
                        rwy_hdg = f'{hdg} - {hdg - 180}'
                    else:
                        rwy_hdg = f'{hdg}°/{hdg + 180}°'

                    draw.text((0, px), f'{curr_rwy} - {len_width} - {rwy_hdg}', (0, 0, 0), font=font,
                              stroke_width=3, stroke_fill=(255, 255, 255))
                    i += 1
                info_embed.add_field(name='Runways:', value=runways[:-3])
                info_embed.add_field(name='Airport Elevation:', value=f'{str(elevation)}ft')
                info_embed.add_field(name='Magnetic Variation:', value=f'{str(mag_var)}°')
                if notime:
                    info_embed.add_field(name='Timezone:', value='N/A')
                else:
                    info_embed.add_field(name='Timezone:', value=f'{offset} UTC, {timezone}')
                img.save('Utils/info_done.png')

            if notime:
                info_embed.add_field(name='Zulu/Local Time:', value=f'Zulu: {utc}\nLocal: N/A')
            else:
                info_embed.add_field(name='Zulu/Local Time:', value=f'Zulu: {utc}\nLocal: {local}')
            info_embed.add_field(name='METAR:', value=metar)
            info_embed.add_field(name='TAF:', value=taf)
            info_embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')

            info_embed.set_image(url='attachment://info_done.png')
            info_embed.set_footer(
                text=f'Using data from the Flight Plan Database (https://flightplandatabase.com), check the full weather for this airport with /metar {icao.upper()}')

            file = discord.File('Utils/info_done.png')

            await ctx.reply(embed=info_embed, file=file, mention_author=False)

    # @commands.command()
    # async def notam(self, ctx, icao: str = 'NO INPUT', page=1):
    #
    #     if len(icao) != 4:
    #         return await ctx.reply("Please input a correct ICAO code", mention_author=False)
    #
    #     if not isinstance(page, int):
    #         return await ctx.reply('Please insert a number for the embed page', mention_author=False)
    #
    #     try:
    #         request = requests.get(
    #             f'https://api.autorouter.aero/v1.0/notam?itemas=["{icao.upper()}"]&offset=0&limit=200', timeout=5)
    #     except Exception as err:
    #         await ctx.reply(
    #             "Timeout error while requesting NOTAMs, API servers are probably offline. Please try again later",
    #             mention_author=False)
    #         return print(err)
    #
    #     if request.status_code != 200:
    #         print(f'Failed to fetch info for {icao.upper()}, error {request.status_code}')
    #         return await ctx.reply(
    #             f"Error {request.status_code} while retrieving NOTAMs for {icao.upper()}, either the website is down or the airport you chose is not available",
    #             mention_author=False)
    #
    #     else:
    #
    #         prfx = get_prefix(bot_client=self, message=ctx.message)
    #
    #         notam = request.json()
    #
    #         notamemb = discord.Embed(
    #             title=f'NOTAM list for **{icao.upper()}**',
    #             description=f"Number of active NOTAMs: {notam['total']}",
    #             colour=discord.Colour.from_rgb(97, 0, 215)
    #         )
    #
    #         # with open('./Utils/notam.json', 'w') as f:
    #         #     json.dump(notam, f, indent=4)
    #
    #         total = notam['total']
    #
    #         numb = 0
    #         page -= 1
    #         i = page * 5
    #
    #         for _ in notam['rows']:
    #             numb += 1
    #
    #         total_pages = math.ceil(total / 5)
    #
    #         if total_pages == 0:
    #             return await ctx.reply(f'No NOTAMs were found for {icao.upper()}!', mention_author=False)
    #
    #         if page + 1 > total_pages:
    #             return await ctx.reply(f'Please select a page number between 1 and {total_pages}', mention_author=False)
    #
    #         try:
    #             while page * 5 <= i < (page * 5) + 5:
    #                 lon = (notam['rows'][i]['lon'] * 90) / (1 << 30)
    #                 lat = (notam['rows'][i]['lat'] * 90) / (1 << 30)
    #                 radius = str(notam['rows'][i]['radius'])
    #                 lon_str = str(int(abs(lon)))
    #                 lat_str = str(int(abs(lat)))
    #
    #                 if len(radius) < 3:
    #                     radius = '0' + radius
    #                     if len(radius) < 3:
    #                         radius = '0' + radius
    #
    #                 if len(lon_str) == 2:
    #                     lon_str = '0' + lon_str
    #                 elif len(lon_str) == 1:
    #                     lon_str = '00' + lon_str
    #
    #                 elif len(lat_str) == 1:
    #                     lat_str = '0' + lat_str
    #
    #                 if lon < 0:
    #                     lon = abs(lon)
    #                     lon_str += str(int(round((lon - int(lon)) * 60, 0)))
    #                     lon_str += 'W'
    #                 else:
    #                     lon_str += str(int(round((lon - int(lon)) * 60, 0)))
    #                     lon_str += 'E'
    #
    #                 if lat < 0:
    #                     lat = abs(lat)
    #                     lat_str += str(int(round((lat - int(lat)) * 60, 0)))
    #                     lat_str += 'S'
    #                 else:
    #                     lat_str += str(int(round((lat - int(lat)) * 60, 0)))
    #                     lat_str += 'N'
    #
    #                 coordinates = lat_str + lon_str + radius
    #
    #                 first_line = str(notam['rows'][i]['series']) + str(notam['rows'][i]['number']) + '/' + str(
    #                     notam['rows'][i]['year']) + ' ' + 'NOTAM' + str(notam['rows'][i]['type']) + ' '
    #
    #                 if notam['rows'][i]['lower'] == 0:
    #                     notam['rows'][i]['lower'] = '000'
    #
    #                 line_q = 'Q) ' + notam['rows'][i]['fir'] + '/' + notam['rows'][i]['code23'] + notam['rows'][i][
    #                     'code45'] + '/' + notam['rows'][i]['traffic'] + '/' + notam['rows'][i]['purpose'] + '/' + \
    #                     notam['rows'][i]['scope'] + '/' + str(notam['rows'][i]['lower']) + '/' + str(
    #                     notam['rows'][i]['upper']) + '/' + coordinates
    #
    #                 if notam['rows'][i]['estimation'] is not None:
    #                     line_abc = f'A) {icao.upper()}' + '    B) ' + datetime.datetime.fromtimestamp(
    #                         notam['rows'][i]['startvalidity']).strftime(
    #                         '%Y-%m-%d %H:%M') + '    C) ' + datetime.datetime.fromtimestamp(
    #                         notam['rows'][i]['endvalidity']).strftime('%Y-%m-%d %H:%M') + ' ' + notam['rows'][i][
    #                                    'estimation']
    #                 else:
    #                     line_abc = f'A) {icao.upper()}' + '    B) ' + datetime.datetime.fromtimestamp(
    #                         notam['rows'][i]['startvalidity']).strftime(
    #                         '%Y-%m-%d %H:%M') + '    C) ' + datetime.datetime.fromtimestamp(
    #                         notam['rows'][i]['endvalidity']).strftime('%Y-%m-%d %H:%M')
    #
    #                 if notam['rows'][i]['referredseries'] is not None:
    #                     first_line += str(notam['rows'][i]['referredseries']) + str(
    #                         notam['rows'][i]['referrednumber']) + '/' + str(notam['rows'][i]['referredyear'])
    #
    #                 notamemb.add_field(
    #                     name=f"{notam['rows'][i]['id']} | Modified at {datetime.datetime.fromtimestamp(notam['rows'][i]['modified']).strftime('%Y-%m-%d %H:%M')}",
    #                     value=f'{first_line}\n'
    #                           f'{line_q}\n'
    #                           f'{line_abc}\n'
    #                           f"E) {notam['rows'][i]['iteme']}", inline=False)
    #                 i += 1
    #
    #         except IndexError:
    #             print('index')
    #
    #         notamemb.set_thumbnail(
    #             url='https://cdn.discordapp.com/attachments/356779184393158657/729351510974267513/plane-travel-icon-rebound2.gif')
    #         notamemb.set_footer(
    #             text=f'Page {page + 1} of {total_pages}, use {prfx}notam {icao.upper()} [page number] to select different pages')
    #
    #         try:
    #             await ctx.send(embed=notamemb)
    #         except discord.HTTPException:
    #             await ctx.reply(
    #                 f'Unfortunately this page has more characters than the max allowed limit of 2000, please try with a different ICAO or a different page',
    #                 mention_author=False)

    @commands.hybrid_command(name='simbrief', description='Returns the last flight plan created in SimBrief')
    @app_commands.describe(username='Your SimBrief username')
    async def simbrief(self, ctx, username: str):

        request = requests.get(f'https://www.simbrief.com/api/xml.fetcher.php?username={username}&json=1')
        if request.status_code == 400:
            error = request.json()
            return await ctx.reply(
                f"Error {request.status_code} while retrieving flight plan for {username}, make sure you entered a correct username\n```{error['fetch']['status']}```",
                mention_author=False)

        else:

            info = request.json()
            # with open('./Utils/simbrief.json', 'w') as f:
            #     json.dump(info, f, indent=4)
            # print(info)

            i = 0
            toc = False

            for _ in info:
                if info['navlog']['fix'][i]['name'] == 'TOP OF CLIMB':
                    toc = True
                    break
                else:
                    i += 1

            desc = f'Generated at: **{datetime.datetime.fromtimestamp(int(info["params"]["time_generated"])).strftime("%H:%M %Y-%m-%d")}**  | AIRAC: **{info["params"]["airac"]}** | Units: **{info["params"]["units"]}**\n\n' \
                   f'FL STEPS: **{info["general"]["stepclimb_string"]}**\n\n' \
                   f'ROUTE: **{info["origin"]["icao_code"]}/{info["origin"]["plan_rwy"]}** {info["general"]["route"]} **{info["destination"]["icao_code"]}/{info["destination"]["plan_rwy"]}**'

            fuel = f'TRIP           {info["fuel"]["enroute_burn"]}\n' \
                   f'CONT           {info["fuel"]["contingency"]}\n' \
                   f'ALTN           {info["fuel"]["alternate_burn"]}\n' \
                   f'FINRES         {info["fuel"]["reserve"]}\n' \
                   f'EXTRA          {info["fuel"]["extra"]}\n' \
                   f'TAXI           {info["fuel"]["taxi"]}\n' \
                   f'BLOCK FUEL     {info["fuel"]["plan_ramp"]}\n'

            payload = f'PAX         {info["weights"]["pax_count"]}\n' \
                      f'CARGO       {round((int(info["weights"]["cargo"]) / 1000), 1)}\n' \
                      f'PAYLOAD     {round((int(info["weights"]["payload"]) / 1000), 1)}\n' \
                      f'ZFW         {round((int(info["weights"]["est_zfw"]) / 1000), 1)}\n' \
                      f'FUEL        {round((int(info["fuel"]["plan_ramp"]) / 1000), 1)}\n' \
                      f'TOW         {round((int(info["weights"]["est_tow"]) / 1000), 1)}\n' \
                      f'LAW         {round((int(info["weights"]["est_ldw"]) / 1000), 1)}\n'
            if toc:
                general = f'Cost Index:         {info["general"]["cruise_profile"]}\n' \
                          f'Route Distance:     {info["general"]["route_distance"]}nm\n' \
                          f'Average Wind:       {info["general"]["avg_wind_dir"]}°/{info["general"]["avg_wind_comp"]}kt\n' \
                          f'Aircraft:           {info["aircraft"]["name"]}\n' \
                          f'Est. Time Enroute:  {round((int(info["times"]["est_time_enroute"]) / 3600), 2)}hrs\n' \
                          f'TOC Conditions:     {info["navlog"]["fix"][i]["wind_dir"]}°/{info["navlog"]["fix"][i]["wind_spd"]}kt | OAT: {info["navlog"]["fix"][i]["oat"]} | ISA DEV: {info["navlog"]["fix"][i]["oat_isa_dev"]}\n'
            else:
                general = f'Cost Index:         {info["general"]["cruise_profile"]}\n' \
                          f'Route Distance:     {info["general"]["route_distance"]}\n' \
                          f'Average Wind:       {info["general"]["avg_wind_dir"]}°/{info["general"]["avg_wind_comp"]}kt\n' \
                          f'Aircraft:           {info["aircraft"]["name"]}\n' \
                          f'Est. Time Enroute:  {info["times"]["est_time_enroute"]}\n'

            directory = info['files']['directory']
            files = f'[X-Plane 11]({directory}{info["fms_downloads"]["xpe"]["link"]}) | [MSFS 2020]({directory}{info["fms_downloads"]["mfs"]["link"]}) | ' \
                    f'[FSX/P3D]({directory}{info["fms_downloads"]["fsx"]["link"]}) | [PMDG]({directory}{info["fms_downloads"]["pmr"]["link"]})'

            sb_embed = discord.Embed(
                title=f'Retrieved SimBrief flight plan: **{info["origin"]["icao_code"]} → {info["destination"]["icao_code"]}**  ALTN: {info["alternate"]["icao_code"]}',
                description=desc,
                colour=discord.Colour.from_rgb(97, 0, 215)
            )

            # sb_embed.set_thumbnail(
            #     url="https://cdn.discordapp.com/attachments/651086904925749252/802617703809548298/ezgif.com-gif-maker_3.gif")
            sb_embed.set_footer(
                text='If you prefer to keep your username private, you can use this command in a private chat')
            sb_embed.add_field(name='Fuel:', value=fuel)
            sb_embed.add_field(name='Weights:', value=payload)
            sb_embed.add_field(name='Info:', value=general)
            sb_embed.add_field(name='Departure METAR:', value=info['weather']['orig_metar'], inline=False)
            sb_embed.add_field(name='Destination METAR:', value=info['weather']['dest_metar'], inline=False)
            sb_embed.add_field(name='FMC Files:', value=files, inline=False)
            try:
                sb_embed.set_image(url=f"{info['images']['directory']}{info['images']['map'][0]['link']}")
            except Exception as err:
                print(err)
            await ctx.reply(embed=sb_embed, mention_author=False)

    @flightplan.error
    async def flp_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.reply(
                'Command on cooldown, please wait a few seconds or wait for the current request to be processed',
                mention_author=False, delete_after=10)

    @metar.error
    async def metar_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.reply(
                'Command on cooldown, please wait a few seconds or wait for the current request to be processed',
                mention_author=False, delete_after=5)


async def setup(client):
    await client.add_cog(FlightSim(client))

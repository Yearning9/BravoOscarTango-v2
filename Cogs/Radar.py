import flightradar24
from discord.ext import commands
from datetime import datetime, timedelta
import json
import discord
import staticmaps
from PIL import ImageFile
from discord import app_commands
from FlightRadar24.api import FlightRadar24API
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
ImageFile.LOAD_TRUNCATED_IMAGES = True


fr = flightradar24.Api()
fr_sec = FlightRadar24API()

def line_color(alt):
    if alt < 11:
        return staticmaps.WHITE
    elif alt < 2000:
        r = 255 - int((alt * 255) / 2000)
        return staticmaps.Color(r, 255, 0)
    elif alt < 10500:
        alt = alt - 2000
        b = int((alt * 255) / 8500)
        return staticmaps.Color(0, 255, b)
    elif alt < 21000:
        alt = alt - 10500
        g = 255 - int((alt * 255) / 10500)
        return staticmaps.Color(0, g, 255)
    elif alt < 38000:
        alt = alt - 21000
        r = int((alt * 255) / 17000)
        return staticmaps.Color(r, 0, 255)
    elif alt < 43000:
        alt = alt - 38000
        b = 255 - int((alt * 255) / 5000)
        return staticmaps.Color(255, 0, b)
    elif 43000 <= alt < 100000:
        return staticmaps.RED
    else:
        return staticmaps.WHITE

class Radar(commands.Cog):

    @commands.hybrid_command(name='flight', description="Shows info for a live flight, or a list of past/scheduled flights if it's not currently live")
    @app_commands.describe(flight_id='Flight number')
    @app_commands.choices(image=[app_commands.Choice(name='🗺 Map', value='map'), app_commands.Choice(name='📈 Graph', value='graph')])
    async def flight(self, ctx, flight_id, image: app_commands.Choice[str] = 'map'):

        await ctx.defer()

        sm = staticmaps.Context()
        sm.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

        flight = fr.get_flight(flight_id)

        json_str = json.dumps(flight)
        flight_data = json.loads(json_str)

        # with open('./Utils/fr24.json', 'w') as f:
        #     json.dump(flight, f, indent=4)
        data = flight_data["result"]["response"]["data"]
        if data is None:
            return await ctx.reply('No flight was found for that flight number', mention_author=False)
        airline = data[0]["airline"]["name"]
        airline_icao = data[0]['airline']['code']['icao']
        numbers = flight_data["result"]["response"]["item"]["current"]
        query = flight_data["result"]["request"]["query"]
        timestamp = flight_data["result"]["response"]["timestamp"]

        cr = flight_data['_api']['copyright']

        ts = datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')

        amount = 0
        live = False
        for i in data:
            amount += 1
            if i['status']['live']:
                live = True
                break

        j = amount - 1
        plane = data[j]["aircraft"]["model"]["text"]

        if live:  # wow, this is a long if statement
            if data[j]['airport']['origin'] is None:
                origin = 'N/A'
                origin_iata = 'N/A'
                origin_ver = 'N/A'
            else:
                origin = data[j]["airport"]["origin"]["code"]["icao"]
                origin_iata = data[j]["airport"]["origin"]["code"]["iata"]
                origin_ver = data[j]['airport']['origin']['name']
            if data[j]['airport']['destination'] is None:
                destination = 'N/A'
                dest_iata = 'N/A'
                dest_ver = 'N/A'
            else:
                destination = data[j]["airport"]["destination"]["code"]["icao"]
                dest_iata = data[j]["airport"]["destination"]["code"]["iata"]
                dest_ver = data[j]["airport"]["destination"]["name"]
            plane_pic = flight_data["result"]["response"]["aircraftImages"][0]["images"]["large"][0]["src"]
            registration = data[j]["aircraft"]["registration"]
            time = data[j]["time"]
            origin_country = data[j]["aircraft"]["country"]["alpha2"]
            flag = origin_country.lower()
            callsign = data[j]["identification"]["callsign"]
            status = data[j]['status']['text']
            if data[j]['status']['icon'] is None:
                st_color = 'black'
            else:
                st_color = data[j]['status']['icon']


            if time['scheduled']['departure'] is not None:
                sched1 = datetime.utcfromtimestamp(time["scheduled"]["departure"]).strftime('%d/%m %H:%M')
            else:
                sched1 = 'N/A'
            if time["scheduled"]["arrival"] is not None:
                sched2 = datetime.utcfromtimestamp(time["scheduled"]["arrival"]).strftime('%d/%m %H:%M')
            else:
                sched2 = 'N/A'
            if time['real']['departure'] is not None:
                act = datetime.utcfromtimestamp(time['real']['departure']).strftime('%d/%m %H:%M')
            else:
                act = 'N/A'
            if time['other']['eta'] is not None:
                eta = datetime.utcfromtimestamp(time['other']['eta']).strftime('%d/%m %H:%M')
            else:
                eta = 'N/A'

            dep = None
            arr = None
            found = False

            if origin != 'N/A' and image == 'map':
                lat1 = data[j]["airport"]["origin"]["position"]["latitude"]
                long1 = data[j]["airport"]["origin"]["position"]["longitude"]
                dep = staticmaps.create_latlng(lat1, long1)
                sm.add_object((staticmaps.ImageMarker(dep, './Utils/Radar/tkof.png', 19, 36)))
            if destination != 'N/A' and image == 'map':
                lat2 = data[j]["airport"]["destination"]["position"]["latitude"]
                long2 = data[j]["airport"]["destination"]["position"]["longitude"]
                arr = staticmaps.create_latlng(lat2, long2)
                sm.add_object((staticmaps.ImageMarker(arr, './Utils/Radar/ldg.png', 19, 36)))

            trail = {}
            sent = None
            ts_list = []
            spd_list = []
            alt_list = []

            live_flight = discord.Embed(
                title='{} [{} | {}]'.format(airline, query, callsign),
                description=f'Status: **:{st_color}_circle: {status}**',
                colour=discord.Colour.from_rgb(97, 0, 215)
            )

            live_flight.set_thumbnail(url=plane_pic)
            live_flight.set_footer(text=cr)
            live_flight.add_field(name='Aircraft type:', value=plane)
            live_flight.add_field(name='Registration:', value=':flag_{}: | {}'.format(flag, registration))
            live_flight.add_field(name='Origin Airport:', value=f'{origin_ver} - {origin}/{origin_iata}', inline=False)
            live_flight.add_field(name='Arrival Airport:', value=f'{dest_ver} - {destination}/{dest_iata}')
            live_flight.add_field(name='Scheduled | Actual Departure (UTC):', value='{} | {}'.format(sched1, act),
                                  inline=False)
            live_flight.add_field(name='Scheduled | Estimated Arrival (UTC):', value='{} | {}'.format(sched2, eta))

            if airline_icao is not None and registration is not None:

                live_flight.set_image(url='https://media.discordapp.net/attachments/736887056344678441/1034525783173115934/loading.gif')
                sent = await ctx.send(embed=live_flight)
                airline_req = fr_sec.get_flights(airline=airline_icao)
                airline_input = str(airline_req).split(',')
                z = 0
                pos = None
                trail = None
                hdg = 0
                alt_list = []
                spd_list = []
                ts_list = []

                while z < len(airline_input):
                    if registration in airline_input[z]:
                        try:
                            plane_req = airline_req[z]
                            detes = fr_sec.get_flight_details(plane_req.id)
                            found = True
                            trail = detes['trail']
                            if image == 'map':
                                hdg = int(trail[0]['hd'] / 10)
                                pos = staticmaps.create_latlng(trail[0]['lat'], trail[0]['lng'])
                            break
                        except TypeError or json.JSONDecodeError:
                            found = False
                            break
                    else:
                        z += 1

                if found:
                    q = 0
                    if image == 'map':
                        while q < len(trail) - 1:
                            tr1 = staticmaps.create_latlng(trail[q]['lat'], trail[q]['lng'])
                            tr2 = staticmaps.create_latlng(trail[q+1]['lat'], trail[q+1]['lng'])
                            alt = trail[q]['alt']
                            sm.add_object(staticmaps.Line([tr1, tr2], color=line_color(alt), width=3))
                            q += 1
                        sm.add_object(staticmaps.ImageMarker(pos, f'./Utils/Radar/plane{hdg}.png', 18, 18))

                    elif image.value == 'graph':
                        while q < len(trail) - 1:
                            alt_list.append(trail[q]['alt'])
                            spd_list.append(trail[q]['spd'])
                            ts_list.append(datetime.fromtimestamp(trail[q]['ts']) - timedelta(hours=2))
                            q += 1

                elif dep is not None and arr is not None and image == 'map':
                    sm.add_object(staticmaps.Line([dep, arr], color=staticmaps.BLUE, width=3))


            elif dep is not None and arr is not None and image == 'map':
                sm.add_object(staticmaps.Line([dep, arr], color=staticmaps.BLUE, width=3))


            if dep is not None or arr is not None or found is True and image == 'map':
                image_map = sm.render_cairo(600, 400)
                image_map.write_to_png('./Utils/map.png')
                file = discord.File('Utils/map.png')
                live_flight.set_image(url='attachment://map.png')
            elif image.value == 'graph':
                fig, ax1 = plt.subplots()
                ax1.set_xlabel('Time (UTC)')
                ax1.set_ylabel('Altitude (ft)')
                ax1.plot(ts_list, alt_list)
                ax1.tick_params(axis='y', labelcolor='blue')
                plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))

                ax1.set_facecolor('#2f3136')

                ax1.set_title(f'{query.upper()} Speed and Altitude graph')
                ax1.grid(True)

                ax2 = ax1.twinx()
                ax2.set_ylabel('Ground speed (kt)')
                ax2.plot(ts_list, spd_list, color='orange')
                ax2.tick_params(axis='y', labelcolor='orange')


                plt.savefig('Utils/plot.png')

                file = discord.File('Utils/plot.png')
                live_flight.set_image(url='attachment://plot.png')
            else:
                file = None

            # if airline == 'Vueling':
            #     airline = 'Vuling'

            if found:

                spd = trail[0]['spd']

                live_alt = trail[0]['alt']

                if live_alt >= 10000:
                    live_alt = f'FL{int(live_alt / 100)}'
                else:
                    live_alt = f'{live_alt} ft'

                live_flight.description += f'\nAltitude: **{live_alt}**\nGround Speed: **{spd} kts**'

                return await sent.edit(embed=live_flight, attachments=[file])

            live_flight.set_image(url='attachment://map.png')
            await ctx.send(embed=live_flight, file=file)
            # if airline == 'Vuling':
            #     await ctx.send('*:pray: Pray for our lord Vuling :pray:*')
            return


        else:

            lista = ''

            for i in data:
                if i['airport']['origin'] is None:
                    origin = 'N/A'
                    origin_iata = 'N/A'
                else:
                    origin = data[j]["airport"]["origin"]["code"]["icao"]
                    origin_iata = data[j]["airport"]["origin"]["code"]["iata"]
                if i['airport']['destination'] is None:
                    destination = 'N/A'
                    dest_iata = 'N/A'
                else:
                    destination = data[j]["airport"]["destination"]["code"]["icao"]
                    dest_iata = data[j]["airport"]["destination"]["code"]["iata"]

                status = i["status"]["text"]
                if i['status']['icon'] is None:
                    st_color = 'black'
                else:
                    st_color = i['status']['icon']
                if i['time']['scheduled']['departure'] is not None:
                    std = datetime.utcfromtimestamp(i['time']['scheduled']['departure']).strftime('%d/%m %H:%M')
                else:
                    std = 'N/A'
                lista += f'**{origin}/{origin_iata} → {destination}/{dest_iata}** | Sched. departure: **{std}** | Status: **:{st_color}_circle: {status}**\n'


            embed = discord.Embed(
                title='{} - {}'.format(airline, query),
                description='\n{}'.format(lista)
            )
            embed.set_footer(text=f'Updated at {ts} UTC | {cr}')
            if airline_icao is not None:
                embed.set_thumbnail(url=f'https://www.flightradar24.com/static/images/data/operators/{airline_icao}_logo0.png')

            return await ctx.reply(f'The flight you requested is not currently live, I have found {numbers} scheduled/past flights', embed=embed, mention_author=False)


async def setup(client):
    await client.add_cog(Radar(client))

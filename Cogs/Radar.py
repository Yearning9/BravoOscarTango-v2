import flightradar24
from discord.ext import commands
from datetime import datetime
import json
import discord
import staticmaps
from PIL import ImageFile
from discord import app_commands

ImageFile.LOAD_TRUNCATED_IMAGES = True


fr = flightradar24.Api()


class Radar(commands.Cog):

    @commands.hybrid_command(name='flight', description="Shows info for a live flight, or a list of past/scheduled flights if it's not currently live")
    @app_commands.describe(flight_id='Flight number')
    async def flight(self, ctx, flight_id):

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

            if origin != 'N/A':
                lat1 = data[j]["airport"]["origin"]["position"]["latitude"]
                long1 = data[j]["airport"]["origin"]["position"]["longitude"]
                dep = staticmaps.create_latlng(lat1, long1)
                sm.add_object((staticmaps.ImageMarker(dep, './Utils/tkof.png', 36, 36)))
            if destination != 'N/A':
                lat2 = data[j]["airport"]["destination"]["position"]["latitude"]
                long2 = data[j]["airport"]["destination"]["position"]["longitude"]
                arr = staticmaps.create_latlng(lat2, long2)
                sm.add_object((staticmaps.ImageMarker(arr, './Utils/ldg.png', 36, 36)))

            if dep is not None and arr is not None:
                sm.add_object(staticmaps.Line([dep, arr], color=staticmaps.BLUE, width=3))
                image = sm.render_cairo(400, 400)
                sm.set_center(dep)
                sm.set_zoom(13)
                image.write_to_png('./Utils/map.png')

                file = discord.File('Utils/map.png')
            else:
                file = None

            # if airline == 'Vueling':
            #     airline = 'Vuling'

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
            live_flight.add_field(name='Scheduled|Actual Departure (UTC):', value='{} | {}'.format(sched1, act),
                                  inline=False)
            live_flight.add_field(name='Scheduled|Estimated Arrival (UTC):', value='{} | {}'.format(sched2, eta),
                                  inline=True)
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

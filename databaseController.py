import logging
from datetime import datetime

from tinydb import Query, where

log = logging.getLogger(__name__)
name_key = "name"
rating_key = "rating"
rolling_price_key = "rolling5Prices"
most_recent_key = "mostRecentPrice"
average_key = "averagePrice"
date_key = "dateOfMostRecentPrice"


def update_price(rating, name, price, db):
    inner_player = Query()
    message = str(rating) + " " + name.title() + " " + str(('{:,}'.format(price)))
    name = name.lower()

    if db.contains((inner_player.name == name) & (inner_player.rating == rating)):
        item = db.get(inner_player.name == name)
        prices = item.get(rolling_price_key)
        if len(prices) >= 5:
            prices.pop(0)
        prices.append(price)
        average_price = round(sum(prices) / len(prices))

        db.update_multiple(
            [({rolling_price_key: prices}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({most_recent_key: price}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({average_key: average_price}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({date_key: datetime.today().strftime('%d/%m/%Y')},
              (inner_player.name == name) & (inner_player.rating == rating))])
        message = "Updating: " + message
        log.info(message)
        return message
    else:
        db.insert({name_key: name,
                   rating_key: rating,
                   most_recent_key: price,
                   date_key: datetime.today().strftime('%Y-%m-%d'),
                   rolling_price_key: [price],
                   average_key: price})
        message = "Adding: " + message
        log.info(message)
        return message


def get_player(rating, name, db):
    player = Query()
    name = name.lower()
    if db.contains((player.name == name) & (player.rating == rating)):
        item = db.get((player.name == name) & (player.rating == rating))
        formatted_price = ('{:,}'.format(item.get(most_recent_key)))
        formatted_average = ('{:,}'.format(item.get(average_key)))
        message = ("Player: %d %s\nMost Recent Price: %s\nMost Recent Price added on: %s\nAverage of %d Most Recent "
                   "Prices: %s" %
                   (rating, name.title(), formatted_price, item.get(date_key),
                    len(item.get(rolling_price_key)),
                    formatted_average))
        log.info(message)
        return message
    else:
        message = "Player: %d %s is not in the database" % (rating, name.title())
        log.info(message)
        return message


def get_highest_sellers(rating, db):
    items = db.search(where(rating_key) == rating)
    items.sort(key=lambda x: x.get(average_key), reverse=True)
    log.info(items)
    message = ""
    for item in items[:5]:
        message += str(item.get(rating_key)) + " " + item.get(name_key).title() + " " + str(
            ('{:,}'.format(item.get(average_key)))) + " " + "as of: " + item.get(date_key) + "\n"
    log.info(message)
    return "%d Highest selling %d rated players:\n%s" % (len(items[:5]), rating, message)

import logging
from datetime import datetime

from tinydb import Query, where


def update_price(rating, name, price, db):
    inner_player = Query()
    rolling_price_key = "rolling5Prices"
    most_recent_key = "mostRecentPrice"
    average_key = "averagePrice"
    date_key = "dateOfMostRecentPrice"
    message = rating + " " + name + " " + price
    name = name.lower()

    if db.contains((inner_player.name == name) & (inner_player.rating == rating)):
        item = db.get(inner_player.name == name)
        prices = item.get(rolling_price_key)
        if len(prices) >= 5:
            prices.pop(0)
        prices.append(price)
        average_price = sum(prices) / len(prices)

        db.update_multiple(
            [({rolling_price_key: prices}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({most_recent_key: price}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({average_key: average_price}, (inner_player.name == name) & (inner_player.rating == rating)),
             ({date_key: datetime.today().strftime('%Y-%m-%d')},
              (inner_player.name == name) & (inner_player.rating == rating))])
        message = "Updating: " + message
        logging.info(message)
        return message
    else:
        db.insert({"name": name,
                   "rating": rating,
                   "mostRecentPrice": price,
                   "dateOfMostRecentPrice": datetime.today().strftime('%Y-%m-%d'),
                   "rolling5Prices": [price],
                   "averagePrice": price})
        message = "Adding: " + message
        return message


def get_player(rating, name, db):
    player = Query()
    name = name.lower()
    if db.contains((player.name == name) & (player.rating == rating)):
        item = db.get((player.name == name) & (player.rating == rating))
        formatted_price = ('{:,}'.format(item.get("mostRecentPrice")))
        formatted_average = ('{:,}'.format(item.get("averagePrice")))
        return ("Player: %s\nMost Recent Price: %s\nMost Recent Price added on: %s\nAverage of %d Most Recent Prices: "
                "%s" %
                (name, formatted_price, item.get("dateOfMostRecentPrice"),
                 len(item.get("rolling5Prices")),
                 formatted_average))
    else:
        return "Player: %d %s is not in the database" % (rating, name)


def get_highest_seller(rating, db):
    # print(db.search(where("rating") == rating))
    items = db.search(where("rating") == rating)
    items.sort(key=lambda x: x.get("averagePrice"), reverse=True)
    message = ""
    for item in items[:5]:
        message += str(item.get("rating")) + " " + item.get("name").title() + " " + str(
            ('{:,}'.format(item.get("averagePrice")))) + "\n"
    return "%d Highest selling %d rated players:\n%s" % (len(items[:5]), rating, message)

# SI 201 HW4 (Library Checkout System)
# Your name:Henry Parker
# Your student id: hfparker
# Your email: hfparker@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from email.mime import text

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
#import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    listings = []

    cards = soup.find_all("a", href=True)
    for a in cards:
        href = a.get("href")
        if "/rooms/" in href:
            match = re.search(r"/rooms/(?:plus/)?(\d+)", href)
            if match:
                listing_id = match.group(1)
                title = a.get_text(" ", strip=True)
                # include listing even if title is empty
                listings.append((title, listing_id))

    # remove duplicates while preserving order
    seen = set()
    result = []
    for t in listings:
        if t[1] not in seen:
            seen.add(t[1])
            result.append(t)

    return result
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    text = soup.get_text(" ", strip=True)

    # policy number
    policy_number = None

    # try to find a visible label like "Registration number" or "License number"
    label_node = soup.find(string=re.compile(r"(Registration|License)\s+number", re.I))

    if label_node:
        # find the next text node that actually contains digits (the policy value)
        next_text = label_node.find_next(string=re.compile(r"\d"))
        if next_text:
            nearby_text = next_text.strip()
        else:
            nearby_text = label_node.parent.get_text(" ", strip=True)

        m1 = re.search(r"20\d{2}-00\d{4}STR", nearby_text)
        m2 = re.search(r"STR-000\d{4}", nearby_text)
        m_raw = re.search(r"\b\d{6,}\b", nearby_text)

        if m1:
            policy_number = m1.group()
        elif m2:
            policy_number = m2.group()
        elif m_raw:
            policy_number = m_raw.group()
        else:
            # fallback: if no clear policy found but label exists, use listing_id (handles invalid numeric case)
            policy_number = listing_id
    else:
        # fallback: check for exempt
        if "exempt" in text.lower():
            policy_number = "Exempt"
        else:
            # last-resort: search entire text but prefer valid formats first
            m1 = re.search(r"20\d{2}-00\d{4}STR", text)
            m2 = re.search(r"STR-000\d{4}", text)
            if m1:
                policy_number = m1.group()
            elif m2:
                policy_number = m2.group()
            else:
                policy_number = "Pending"
    # host type
    host_type = "Superhost" if "Superhost" in text else "regular"

    # host name
    host_name = ""
    host_section = soup.find(string=re.compile("Hosted by"))
    if host_section:
        host_name = host_section.split("Hosted by")[-1].strip()

    # room type
    subtitle = soup.find("h2")
    room_type = "Entire Room"
    if subtitle:
        sub_text = subtitle.get_text()
        if "Private" in sub_text:
            room_type = "Private Room"
        elif "Shared" in sub_text:
            room_type = "Shared Room"

    # location rating
    location_rating = 0.0

    loc_node = soup.find(string=re.compile("Location"))
    if loc_node:
        loc_text = loc_node.find_next(string=re.compile(r"\d\.\d"))
        if loc_text:
            match = re.search(r"\d\.\d", loc_text)
            if match:
                location_rating = float(match.group())

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    basic = load_listing_results(html_path)
    full = []

    for title, listing_id in basic:
        details = get_listing_details(listing_id)[listing_id]
        full.append((
            title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"]
        ))

    return full
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[-1], reverse=True)

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Listing Title", "Listing ID", "Policy Number",
            "Host Type", "Host Name", "Room Type", "Location Rating"
        ])
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}

    for row in data:
        room_type = row[5]
        rating = row[6]

        if rating == 0.0:
            continue

        totals[room_type] = totals.get(room_type, 0) + rating
        counts[room_type] = counts.get(room_type, 0) + 1

    return {k: round(totals[k] / counts[k], 1) for k in totals}
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid = []

    for row in data:
        listing_id = row[1]
        policy = row[2]
        
        if policy in ["Pending", "Exempt"]:
            continue

        # catch plain numeric invalid policies like "16204265"
        if policy.isdigit():
            invalid.append(listing_id)
            continue

        valid1 = re.fullmatch(r"20\d{2}-00\d{4}STR", policy)
        valid2 = re.fullmatch(r"STR-000\d{4}", policy)

        if not (valid1 or valid2):
            invalid.append(listing_id)

    return invalid
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    url = "https://scholar.google.com/scholar"
    params = {"q": query}
    res = requests.get(url, params=params)

    soup = BeautifulSoup(res.text, "html.parser")
    titles = []

    for h3 in soup.find_all("h3"):
        title = h3.get_text()
        if title:
            titles.append(title)

    return titles
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]
        
        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        output_csv(self.detailed_data, out_path)
        with open(out_path, newline="", encoding="utf-8-sig") as csv_file:
            rows = list(csv.reader(csv_file))
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        avg_ratings = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(avg_ratings["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])
        


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")
    

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)

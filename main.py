import json
import time
from io import StringIO
from copy import deepcopy
from datetime import datetime

import streamlit as st


def show_intro() -> None:
    st.title("🎈 _Mega_ Zap⚡️!")


def _record_upload(label: str) -> dict:
    record = {}
    upload = st.file_uploader(label, type=["json"])
    if upload is not None:
        record = json.loads(StringIO(upload.getvalue().decode("utf-8")).read())
    return record


def _process_identifiers(
    series: dict,
    side_a: dict,
    side_b: dict,
    isbn_flat: str | None,
    isbn_folded: str | None,
):
    id_isbn_flat = (
        {"identifier": f"{isbn_flat} (Flat)", "namespace": "isbn"}
        if isbn_flat
        else None
    )
    id_isbn_folded = (
        {"identifier": f"{isbn_folded} (Folded)", "namespace": "isbn"}
        if isbn_folded
        else None
    )

    for record in [series, side_a, side_b]:
        for isbn in [id_isbn_flat, id_isbn_folded]:
            if isbn:
                record["identification"]["identifiers"].append(isbn)


def _process_contacts(series: dict, side_a: dict, side_b: dict):
    for record in [series, side_a, side_b]:
        for i, contact in enumerate(record["identification"]["contacts"]):
            if (
                contact["email"] == "magic@bas.ac.uk"
                and "author" not in contact["role"]
            ):
                record["identification"]["contacts"][i]["role"].append("author")


def _cp_graphic(graphic: dict, id: str) -> dict:
    graphic_copy = deepcopy(graphic)
    graphic_copy["identifier"] = id
    return graphic_copy


def _process_graphic_overviews(series: dict, side_a: dict, side_b: dict):
    s = series["identification"]["graphic_overviews"][0]
    a = side_a["identification"]["graphic_overviews"][0]
    b = side_b["identification"]["graphic_overviews"][0]

    series["identification"]["graphic_overviews"] = [
        s,
        _cp_graphic(a, "side_a"),
        _cp_graphic(b, "side_b"),
    ]
    side_a["identification"]["graphic_overviews"] = [a, _cp_graphic(s, "covers")]
    side_b["identification"]["graphic_overviews"] = [b, _cp_graphic(s, "covers")]


def _process_aggregations(series: dict, side_a: dict, side_b: dict) -> None:
    id_series = series["file_identifier"]
    id_a = side_a["file_identifier"]
    id_b = side_b["file_identifier"]

    series["identification"]["aggregations"].extend(
        [
            {
                "identifier": {
                    "identifier": id_a,
                    "href": f"https://data.bas.ac.uk/items/{id_a}",
                    "namespace": "data.bas.ac.uk",
                },
                "association_type": "isComposedOf",
                "initiative_type": "paperMap",
            },
            {
                "identifier": {
                    "identifier": id_b,
                    "href": f"https://data.bas.ac.uk/items/{id_b}",
                    "namespace": "data.bas.ac.uk",
                },
                "association_type": "isComposedOf",
                "initiative_type": "paperMap",
            },
        ]
    )
    side_a["identification"]["aggregations"] = [
        {
            "identifier": {
                "identifier": id_series,
                "href": f"https://data.bas.ac.uk/items/{id_series}",
                "namespace": "data.bas.ac.uk",
            },
            "association_type": "largerWorkCitation",
            "initiative_type": "paperMap",
        },
        {
            "identifier": {
                "identifier": id_b,
                "href": f"https://data.bas.ac.uk/items/{id_b}",
                "namespace": "data.bas.ac.uk",
            },
            "association_type": "physicalReverseOf",
            "initiative_type": "paperMap",
        },
    ]
    side_b["identification"]["aggregations"] = [
        {
            "identifier": {
                "identifier": id_series,
                "href": f"https://data.bas.ac.uk/items/{id_series}",
                "namespace": "data.bas.ac.uk",
            },
            "association_type": "largerWorkCitation",
            "initiative_type": "paperMap",
        },
        {
            "identifier": {
                "identifier": id_a,
                "href": f"https://data.bas.ac.uk/items/{id_a}",
                "namespace": "data.bas.ac.uk",
            },
            "association_type": "physicalReverseOf",
            "initiative_type": "paperMap",
        },
    ]


def resolve_bboxes(
    bboxes: list[tuple[float, float, float, float]],
) -> tuple[float, float, float, float]:
    west = min([bbox[0] for bbox in bboxes])
    east = max([bbox[1] for bbox in bboxes])
    south = min([bbox[2] for bbox in bboxes])
    north = max([bbox[3] for bbox in bboxes])

    return (west, east, south, north)


def _process_extent(series: dict, side_a: dict, side_b: dict):
    a = deepcopy(side_a["identification"]["extents"][0])
    b = deepcopy(side_b["identification"]["extents"][0])
    a["identifier"] = "side-a"
    b["identifier"] = "side-b"

    bbboxes = [
        (
            extent["geographic"]["bounding_box"]["west_longitude"],
            extent["geographic"]["bounding_box"]["east_longitude"],
            extent["geographic"]["bounding_box"]["south_latitude"],
            extent["geographic"]["bounding_box"]["north_latitude"],
        )
        for extent in [a, b]
    ]
    bbox = resolve_bboxes(bbboxes)
    bounding = {
        "identifier": "bounding",
        "geographic": {
            "bounding_box": {
                "west_longitude": bbox[0],
                "east_longitude": bbox[1],
                "south_latitude": bbox[2],
                "north_latitude": bbox[3],
            }
        },
    }

    series["identification"]["extents"] = [bounding, a, b]


def _process_distribution(series: dict):
    pub_maps_dist_option = {
        "distributor": {
            "organisation": {
                "name": "Mapping and Geographic Information Centre, British Antarctic Survey",
                "href": "https://ror.org/01rhff309",
                "title": "ror",
            },
            "phone": "+44 (0)1223 221400",
            "address": {
                "delivery_point": "British Antarctic Survey, High Cross, Madingley Road",
                "city": "Cambridge",
                "administrative_area": "Cambridgeshire",
                "postal_code": "CB3 0ET",
                "country": "United Kingdom",
            },
            "email": "magic@bas.ac.uk",
            "online_resource": {
                "href": "https://www.bas.ac.uk/teams/magic",
                "title": "Mapping and Geographic Information Centre (MAGIC) - BAS public website",
                "description": "General information about the BAS Mapping and Geographic Information Centre (MAGIC) from the British Antarctic Survey (BAS) public website.",
                "function": "information",
            },
            "role": ["distributor"],
        },
        "transfer_option": {
            "online_resource": {
                "href": "https://www.bas.ac.uk/data/our-data/maps/how-to-order-a-map/",
                "title": "Map ordering information - BAS public website",
                "description": "Access information on how to order item.",
                "function": "order",
            }
        },
    }
    series["distribution"] = [pub_maps_dist_option]


def _process_date_stamp(series: dict, side_a: dict, side_b: dict) -> None:
    now = datetime.now()
    for record in [series, side_a, side_b]:
        record["metadata"]["date_stamp"] = now.strftime("%Y-%m-%d")


def _process_records(
    series_in: dict,
    side_a_in: dict,
    side_b_in: dict,
    isbn_flat: str | None,
    isbn_folded: str | None,
) -> tuple[dict, dict, dict]:
    series = deepcopy(series_in)
    side_a = deepcopy(side_a_in)
    side_b = deepcopy(side_b_in)

    with st.status("Processing records...", expanded=True) as status:
        st.write("Setting identifiers...")
        _process_identifiers(series, side_a, side_b, isbn_flat, isbn_folded)
        st.write("Identifiers set.")

        st.write("Setting contacts...")
        _process_contacts(series, side_a, side_b)
        st.write("Contacts set.")

        st.write("Setting graphic overviews...")
        _process_graphic_overviews(series, side_a, side_b)
        st.write("Graphic overviews set.")

        st.write("Setting aggregations...")
        _process_aggregations(series, side_a, side_b)
        st.write("Aggregations set.")

        st.write("Setting extents...")
        _process_extent(series, side_a, side_b)
        st.write("Extents set.")

        st.write("Setting distribution options...")
        _process_distribution(series)
        st.write("Distribution options set.")

        st.write("Setting metadata date stamp...")
        _process_date_stamp(series, side_a, side_b)
        st.write("Metadata date stamp set.")

        time.sleep(0.2)
        status.update(label="Records Processed", state="complete", expanded=False)

    return series, side_a, side_b


def form() -> None:
    st.subheader("Upload records from Zap ⚡️")
    series_in = _record_upload("Record for overall map")
    a_in = _record_upload("Record for side A")
    b_in = _record_upload("Record for side B")

    st.subheader("Set optional ISBNs")
    isbn_flat = st.text_input("ISBN (Flat)")
    isbn_folded = st.text_input("ISBN (Folded)")

    series_out, a_out, b_out = {}, {}, {}
    if series_in and a_in and b_in:
        series_out, a_out, b_out = _process_records(
            series_in, a_in, b_in, isbn_flat, isbn_folded
        )

    if series_out or a_out or b_out:
        st.subheader("Download processed records")

    if series_out:
        st.download_button(
            label="Download Overall Map Record",
            data=json.dumps(series_out, indent=2),
            file_name=f"{series_out['file_identifier']}.json",
            mime="application/json",
            icon=":material/download:",
        )
    if a_out:
        st.download_button(
            label="Download Side A Record",
            data=json.dumps(a_out, indent=2),
            file_name=f"{a_out['file_identifier']}.json",
            mime="application/json",
            icon=":material/download:",
        )
    if b_out:
        st.download_button(
            label="Download Side B Record",
            data=json.dumps(b_out, indent=2),
            file_name=f"{b_out['file_identifier']}.json",
            mime="application/json",
            icon=":material/download:",
        )


def main():
    st.set_page_config()
    show_intro()
    form()


if __name__ == "__main__":
    main()

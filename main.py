import json
import time
from io import StringIO
from copy import deepcopy
from datetime import datetime

import streamlit as st
from streamlit_sortables import sort_items as st_sortables


def show_intro() -> None:
    st.title("_MEGA_ Zap⚡️")


def _record_upload(label: str) -> dict:
    record = {}
    upload = st.file_uploader(label, type=["json"])
    if upload is not None:
        record = json.loads(StringIO(upload.getvalue().decode("utf-8")).read())
    return record


def _process_hierarchy_level(series: dict) -> None:
    series["hierarchy_level"] = "paperMapProduct"


def _process_identifiers(
    series: dict, side_a: dict, side_b: dict, isbn_flat: str | None, isbn_folded: str | None
) -> None:
    id_isbn_flat = {"identifier": f"{isbn_flat} (Flat)", "namespace": "isbn"} if isbn_flat else None
    id_isbn_folded = {"identifier": f"{isbn_folded} (Folded)", "namespace": "isbn"} if isbn_folded else None

    for record in [series, side_a, side_b]:
        for isbn in [id_isbn_flat, id_isbn_folded]:
            if isbn:
                record["identification"]["identifiers"].append(isbn)


def _process_contacts(
    series: dict, side_a: dict, side_b: dict, contacts_order: tuple[list[int], list[int], list[int]]
) -> None:
    for record in [series, side_a, side_b]:
        # set roles for MAGIC contact
        for i, contact in enumerate(record["identification"]["contacts"]):
            if contact.get("email", "") == "magic@bas.ac.uk" and "author" not in contact["role"]:
                record["identification"]["contacts"][i]["role"].append("author")

    # reorder contacts
    series["identification"]["contacts"] = [series["identification"]["contacts"][i] for i in contacts_order[0]]
    side_a["identification"]["contacts"] = [side_a["identification"]["contacts"][i] for i in contacts_order[1]]
    side_b["identification"]["contacts"] = [side_b["identification"]["contacts"][i] for i in contacts_order[2]]


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


def resolve_bboxes(bboxes: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float]:
    west = min([bbox[0] for bbox in bboxes])
    east = max([bbox[1] for bbox in bboxes])
    south = min([bbox[2] for bbox in bboxes])
    north = max([bbox[3] for bbox in bboxes])

    return (west, east, south, north)


def _process_extent(series: dict, side_a: dict, side_b: dict) -> None:
    a = deepcopy(next(extent for extent in side_a["identification"]["extents"] if extent["identifier"] == "bounding"))
    b = deepcopy(next(extent for extent in side_b["identification"]["extents"] if extent["identifier"] == "bounding"))

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

    series["identification"]["extents"] = [bounding]


def _set_sheet_number(record: dict, sheet_number: str) -> None:
    sinfo = {}
    if "supplemental_information" in record["identification"]:
        # try to json decode existing supplemental information
        try:
            sinfo = json.loads(record["identification"]["supplemental_information"])
        except json.JSONDecodeError:
            msg = "Supplemental information is set but isn't JSON parsable, won't continue."
            e = RuntimeError(msg)
            st.exception(e)
            raise e
        sinfo["sheet_number"] = sheet_number
        record["identification"]["supplemental_information"] = json.dumps(sinfo)


def _process_sheet_number(series: dict, side_a: dict, side_b: dict, sheet_number: str | None) -> None:
    if not sheet_number:
        return

    _set_sheet_number(series, sheet_number)
    _set_sheet_number(side_a, f"{sheet_number}A")
    _set_sheet_number(side_b, f"{sheet_number}B")


def _process_distribution(series: dict, side_a: dict, side_b: dict) -> None:
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
    for record in [series, side_a, side_b]:
        record["distribution"] = [pub_maps_dist_option]


def _process_date_stamp(series: dict, side_a: dict, side_b: dict) -> None:
    now = datetime.now()
    for record in [series, side_a, side_b]:
        record["metadata"]["date_stamp"] = now.strftime("%Y-%m-%d")


def _process_records(
    series_in: dict,
    side_a_in: dict,
    side_b_in: dict,
    sheet_number: str | None,
    isbn_flat: str | None,
    isbn_folded: str | None,
    contacts_order: tuple[list[int], list[int], list[int]],
) -> tuple[dict, dict, dict]:
    series = deepcopy(series_in)
    side_a = deepcopy(side_a_in)
    side_b = deepcopy(side_b_in)

    with st.status("Processing records...", expanded=True) as status:
        _process_hierarchy_level(series)
        st.write("Hierarchy level set.")

        _process_identifiers(series, side_a, side_b, isbn_flat, isbn_folded)
        st.write("Identifiers set (if configured).")

        _process_contacts(series, side_a, side_b, contacts_order)
        st.write("Contacts set.")

        _process_aggregations(series, side_a, side_b)
        st.write("Aggregations set.")

        _process_extent(series, side_a, side_b)
        st.write("Extents set.")

        _process_sheet_number(series, side_a, side_b, sheet_number)
        st.write("Sheet number set (if configured).")

        _process_distribution(series, side_a, side_b)
        st.write("Distribution options set.")

        _process_date_stamp(series, side_a, side_b)
        st.write("Metadata date stamp set.")

        time.sleep(0.2)
        status.update(label="Records Processed", state="complete", expanded=False)

    return series, side_a, side_b


def _record_contact_names(record: dict) -> list[str]:
    return [
        contact["individual"]["name"] if "individual" in contact else contact["organisation"]["name"]
        for contact in record["identification"]["contacts"]
    ]


def _process_contact_indexes(record: dict, sorted_names: list[str]):
    indexes = [
        record["identification"]["contacts"].index(
            next(
                contact
                for contact in record["identification"]["contacts"]
                if (
                    ("individual" in contact and contact["individual"]["name"] == name)
                    or ("organisation" in contact and contact["organisation"]["name"] == name)
                )
            )
        )
        for name in sorted_names
    ]
    return indexes


def _form_contacts(series: dict, side_a: dict, side_b: dict) -> tuple[list[int], list[int], list[int]]:
    """
    Reorders contacts in records.

    In general returns a list of new indexes giving the desired order of contacts in a record.

    E.g. for an orginial list [0, 1, 2] where the middle item is moved to the end, [0, 2, 1] is returned.
    To re-order a list, access the original list using the new list (`new = [original[i] for i in updated_indexes]`)

    Where all records have the same contacts, a single input is shown (for the series record) and the same indexes are
    returned for all three records. Where any different, separate inputs and indexes are used.
    """
    series_contacts = _record_contact_names(series)
    contacts_a = _record_contact_names(side_a)
    contacts_b = _record_contact_names(side_b)

    if sorted(series_contacts) == sorted(contacts_a) == sorted(contacts_b):
        # contacts are the same across records, so we can show one input
        series_names_sorted = st_sortables(series_contacts)
        series_indexes = _process_contact_indexes(series, series_names_sorted)
        return series_indexes, series_indexes, series_indexes

    st.write("Series contacts:")
    series_names_sorted = st_sortables(series_contacts)
    st.write("Side A contacts:")
    a_names_sorted = st_sortables(contacts_a)
    st.write("Side B contacts:")
    b_names_sorted = st_sortables(contacts_b)

    series_indexes = _process_contact_indexes(series, series_names_sorted)
    a_indexes = _process_contact_indexes(side_a, a_names_sorted)
    b_indexes = _process_contact_indexes(side_b, b_names_sorted)
    return series_indexes, a_indexes, b_indexes


def form() -> None:
    st.subheader("Upload Zap ⚡️ records")
    series_in = _record_upload("Overall map")
    a_in = _record_upload("Side A")
    b_in = _record_upload("Side B")

    if not series_in or not a_in or not b_in:
        st.info("Set records to continue.")
        return

    st.subheader("Set optional sheet number")
    st.write("Map series and edition can be set in Zap ⚡️.")
    sheet_number = st.text_input("Sheet number")
    st.write(
        f"Sheet numbers will be set as *{sheet_number}*, *{sheet_number}A* and *{sheet_number}B* in records respectively."
    )

    st.subheader("Set optional ISBNs")
    isbn_flat = st.text_input("ISBN (Flat)")
    isbn_folded = st.text_input("ISBN (Folded)")

    st.subheader("Set authors order")
    contact_indexes = _form_contacts(series_in, a_in, b_in)

    st.info("Changing any options above will automatically re-process records for download.")
    series_out, a_out, b_out = {}, {}, {}
    series_out, a_out, b_out = _process_records(
        series_in, a_in, b_in, sheet_number, isbn_flat, isbn_folded, contact_indexes
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


def main() -> None:
    st.set_page_config()
    show_intro()
    form()


if __name__ == "__main__":
    main()

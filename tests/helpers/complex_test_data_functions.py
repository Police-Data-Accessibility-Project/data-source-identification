from collector_db.enums import URLMetadataAttributeType, ValidationSource, ValidationStatus
from core.enums import RecordType
from tests.helpers.DBDataCreator import DBDataCreator


async def setup_for_get_next_url_for_final_review(
        db_data_creator: DBDataCreator,
        annotation_count: int,
        include_user_annotations: bool = True
):
    """
    Sets up the database to test the final_review functions
    Auto-labels the URL with 'relevant=True' and 'record_type=ARREST_RECORDS'
    And applies auto-generated user annotations
    """

    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0]
    await db_data_creator.html_data([url_mapping.url_id])

    async def add_metadata_annotation(count: int, value: str, metadata_id: int):
        for i in range(count):
            await db_data_creator.user_annotation(
                metadata_id=metadata_id,
                annotation=value
        )

    async def add_user_suggestion(count: int):
        agency_id = await db_data_creator.agency()
        for i in range(count):
            await db_data_creator.agency_user_suggestions(
                url_id=url_mapping.url_id,
                agency_id=agency_id
        )

    relevant_metadata_ids = await db_data_creator.metadata(
        url_ids=[url_mapping.url_id],
        attribute=URLMetadataAttributeType.RELEVANT,
        value="True",
        validation_source=ValidationSource.MACHINE_LEARNING,
        validation_status=ValidationStatus.PENDING_VALIDATION
    )
    relevant_metadata_id = relevant_metadata_ids[0]
    record_type_metadata_ids = await db_data_creator.metadata(
        url_ids=[url_mapping.url_id],
        attribute=URLMetadataAttributeType.RECORD_TYPE,
        value=RecordType.ARREST_RECORDS.value,
        validation_source=ValidationSource.MACHINE_LEARNING,
        validation_status=ValidationStatus.PENDING_VALIDATION
    )
    record_type_metadata_id = record_type_metadata_ids[0]

    if include_user_annotations:
        await add_metadata_annotation(annotation_count, "True", relevant_metadata_id)
        await add_metadata_annotation(1, "False", relevant_metadata_id)
        await add_metadata_annotation(3, RecordType.ARREST_RECORDS.value, record_type_metadata_id)
        await add_metadata_annotation(2, RecordType.DISPATCH_RECORDINGS.value, record_type_metadata_id)
        await add_metadata_annotation(1, RecordType.ACCIDENT_REPORTS.value, record_type_metadata_id)

    if include_user_annotations:
        # Add user suggestions for agencies, one suggested by 3 users, another by 2, another by 1
        for i in range(annotation_count):
            await add_user_suggestion(i + 1)


    return url_mapping

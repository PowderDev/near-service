from py_near.models import TransactionResult


def get_tx_error_name(tx_result: TransactionResult):
    error_kind = tx_result.status['Failure'].get('ActionError', {}).get('kind', {})
    error_name = list(error_kind)[0] if len(list(error_kind)) > 0 else "Unknown error"
    return error_name

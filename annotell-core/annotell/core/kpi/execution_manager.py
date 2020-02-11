from annotell.core.kpi.kpi import KPI

def submit_kpi_results(kpis):
    """
    Used to report results to results database once KPI script has executed.
    All results submitted need to be of type Kpi.

    Parameters
    ----------
    :param kpis:
    """

    for kpi in kpis:
        if not isinstance(kpi, KPI):
            raise ValueError("Trying to submit something which is not a result: {}".format(result))

        for result in kpi.get_results():
            print("stub for submitting results, this will be done via HTTPS calls to result storage API once deployed")
            print("result: {}".format(result))

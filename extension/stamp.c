#include <stdio.h>
#include <time.h>
#include "postgres.h"
#include "utils/rel.h"
#include "executor/spi.h"
#include "commands/trigger.h"
#include "utils/fmgrprotos.h"
#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif

extern Datum stamp(PG_FUNCTION_ARGS);

PG_FUNCTION_INFO_V1(trig_test);

Datum
stamp(PG_FUNCTION_ARGS)
{
    TriggerData *trigdata = (TriggerData *) fcinfo->context;
    //TupleDesc   tupdesc;
    HeapTuple   tuple;
    HeapTuple   rettuple;
    int         attnum = 0;
    Datum       datumVal;

    //Get the structure of the tuple in the table.
    //tupdesc = trigdata->tg_relation->rd_att;

    //Make sure that the function is called from a trigger
    if (!CALLED_AS_TRIGGER(fcinfo))
        elog(ERROR, "are you sure you are calling from trigger manager?");

    //If the trigger is part of an UPDATE event
    if (TRIGGER_FIRED_BY_UPDATE(trigdata->tg_event))
    {
        //attnum = SPI_fnumber(tupdesc,"update_ts");
        attnum = 3;
        tuple = trigdata->tg_newtuple;
    }
    else   //If the trigger is part of INSERT event
    {
        //attnum = SPI_fnumber(tupdesc,"insert_ts");
        attnum = 2;
        tuple = trigdata->tg_trigtuple;
    }
    //Get the current timestamp using "now"
    datumVal = DirectFunctionCall3(timestamp_in, CStringGetDatum("now"), ObjectIdGetDatum(InvalidOid), Int32GetDatum(-1));

    //Connect to Server and modify the tuple
    SPI_connect();
    rettuple = SPI_modifytuple(trigdata->tg_relation, tuple, 1, &attnum, &datumVal, NULL);
    if (rettuple == NULL)
    {
        if (SPI_result == SPI_ERROR_ARGUMENT || SPI_result == SPI_ERROR_NOATTRIBUTE)
                elog(ERROR, "SPI_result failed! SPI_ERROR_ARGUMENT or SPI_ERROR_NOATTRIBUTE");
         elog(ERROR, "SPI_modifytuple failed!");
    }
    SPI_finish();                           /* don't forget say Bye to SPI mgr */
    return PointerGetDatum(rettuple);
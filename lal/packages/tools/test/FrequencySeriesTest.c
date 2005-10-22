/*
 * Note that low-level sequence manipulation is tested in the Sequence
 * verification code.  The object here is mostly to test meta-data
 * manipulation.
 */

#include <stdio.h>
#include <stdlib.h>

#include <lal/Date.h>
#include <lal/LALDatatypes.h>
#include <lal/Sequence.h>
#include <lal/FrequencySeries.h>
#include <lal/Units.h>

static LIGOTimeGPS gps_zero = LIGOTIMEGPSZERO;


static REAL4FrequencySeries *random_frequencyseries(size_t n)
{
	REAL4FrequencySeries *s = XLALCreateREAL4FrequencySeries("blah", &gps_zero, 0.0, 1.0 / n, &lalDimensionlessUnit, n);

	while(n--)
		s->data->data[n] = rand() / (float) RAND_MAX;
	return(s);
}


static INT4FrequencySeries *sequential_frequencyseries(size_t n)
{
	INT4FrequencySeries *s = XLALCreateINT4FrequencySeries("blah", &gps_zero, 0.0, 1.0 / n, &lalDimensionlessUnit, n);

	while(n--)
		s->data->data[n] = n;
	return(s);
}


static int cmp_real4(REAL4 *a, REAL4 *b, size_t n)
{
	REAL4 d;

	while(n--) {
		d = *a - *b;
		if(d < 0.0)
			return(-1);
		if(d > 0.0)
			return(+1);
	}
	return(0);
}


int main(int argc, char *argv[])
{
	REAL4FrequencySeries *x, *y;
	INT4FrequencySeries *a;
	int i;

	/*
	 * Destroy
	 */

	/* NULL pointer */
	XLALDestroyREAL4FrequencySeries(NULL);

	/* Incompletely/Incorrectly initialized structure */
	x = malloc(sizeof(*x));
	x->data = NULL;
	XLALDestroyREAL4FrequencySeries(x);
	x = malloc(sizeof(*x));
	x->data = malloc(sizeof(*x->data));
	x->data->data = NULL;
	XLALDestroyREAL4FrequencySeries(x);


	/*
	 * Create
	 */

	/* try segfaulting on array access */
	x = XLALCreateREAL4FrequencySeries("blah", &gps_zero, 0.0, 1.0 / 1, &lalDimensionlessUnit, 1);
	x->data->data[0] = 1.0;
	if((x->f0 != 0.0) || (x->deltaF != 1.0) || (x->data->length != 1) || (x->data->data[0] != 1.0)) {
		fprintf(stderr, "Create test 1 failed\n");
		exit(1);
	}
	XLALDestroyREAL4FrequencySeries(x);

	/*
	 * Cut
	 */

	/* check metadata */
	x = random_frequencyseries(1024);
	y = XLALCutREAL4FrequencySeries(x, 256, 512);
	if((y->deltaF != x->deltaF) || (y->f0 != x->f0 + 256 * x->deltaF) || cmp_real4(x->data->data + 256, y->data->data, 512) || (XLALGPSDiff(&x->epoch, &y->epoch) != 0)) {
		fprintf(stderr, "Cut test 1 failed\n");
		exit(1);
	}
	XLALDestroyREAL4FrequencySeries(x);
	XLALDestroyREAL4FrequencySeries(y);

	/*
	 * Shrink
	 */

	/* check metadata */
	a = sequential_frequencyseries(1024);
	XLALShrinkINT4FrequencySeries(a, 256, 512);
	for(i = 0; i < (int) a->data->length; i++)
		if(a->data->data[i] != i + 256) {
			fprintf(stderr, "Resize test 1a failed\n");
			exit(1);
		}
	if((a->data->length != 512) || (a->f0 != 256 * a->deltaF)) {
		fprintf(stderr, "Resize test 1b failed\n");
		exit(1);
	}
	XLALDestroyINT4FrequencySeries(a);

	/*
	 * Add
	 */

	/* add a series to itself */
	a = sequential_frequencyseries(1024);
	XLALAddINT4FrequencySeries(a, a);
	for(i = 0; i < (int) a->data->length; i++)
		if(a->data->data[i] != 2 * i) {
			fprintf(stderr, "Add test 1 failed\n");
			exit(1);
		}
	XLALDestroyINT4FrequencySeries(a);

	/* add identical data */
	x = random_frequencyseries(1024);
	y = XLALCutREAL4FrequencySeries(x, 0, x->data->length);
	XLALAddREAL4FrequencySeries(x, y);
	for(i = 0; i < (int) x->data->length; i++)
		if(x->data->data[i] != 2 * y->data->data[i]) {
			fprintf(stderr, "Add test 2 failed\n");
			exit(1);
		}
	XLALDestroyREAL4FrequencySeries(x);
	XLALDestroyREAL4FrequencySeries(y);

	/*
	 * Subtract
	 */

	/* subtract a series from itself */
	a = sequential_frequencyseries(1024);
	XLALSubtractINT4FrequencySeries(a, a);
	for(i = 0; i < (int) a->data->length; i++)
		if(a->data->data[i] != 0) {
			fprintf(stderr, "Subtract test 1 failed\n");
			exit(1);
		}
	XLALDestroyINT4FrequencySeries(a);

	/* subtract identical data */
	x = random_frequencyseries(1024);
	y = XLALCutREAL4FrequencySeries(x, 0, x->data->length);
	XLALSubtractREAL4FrequencySeries(x, y);
	for(i = 0; i < (int) x->data->length; i++)
		if(x->data->data[i] != 0.0) {
			fprintf(stderr, "Subtract test 2 failed\n");
			exit(1);
		}
	XLALDestroyREAL4FrequencySeries(x);
	XLALDestroyREAL4FrequencySeries(y);

	/*
	 * Success
	 */

	exit(0);
}

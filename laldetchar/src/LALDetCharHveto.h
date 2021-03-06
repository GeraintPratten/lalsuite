/*
 *  Copyright (C) 2012 Chris Pankow
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with with program; see the file COPYING. If not, write to the
 *  Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
 *  MA  02111-1307  USA
 */

#ifndef _LALDETCHARHVETO_H
#define _LALDETCHARHVETO_H

#include <stdio.h>
#include <math.h>

#include <gsl/gsl_sf.h>

#include <lal/LALString.h>
#include <lal/LALDetCharGlibTypes.h>
#include <lal/LIGOLwXMLBurstRead.h>
#include <lal/LIGOMetadataTables.h>
#include <lal/SnglBurstUtils.h>

#include <lal/Segments.h>

#ifdef  __cplusplus
extern "C" {
#endif

void XLALDetCharScanTrigs( LALGHashTable *chancount, LALGHashTable *chantable, LALGSequence* trig_sequence, const char* chan, double twind, int coinctype );
double XLALDetCharVetoRound( char** winner, LALGHashTable* chancount, LALGHashTable* chanhist, const char* chan, double t_ratio );
void XLALDetCharPruneTrigs( LALGSequence* trig_sequence, const LALSegList* onsource, double snr_thresh, const char* refchan );
void XLALDetCharRemoveTrigs( LALGSequence* trig_sequence, LALGSequence** tbd, const LALSeg veto, const char* vchan, const char* refchan, double snr_thresh );
void XLALDetCharTrigsToVetoList( LALSegList* vetoes, LALGSequence* trig_sequence, const LALSeg veto, const char* vchan );
double XLALDetCharHvetoSignificance( double mu, int k );

#ifdef  __cplusplus
}
#endif

#endif /* _LALDETCHARHVETO_H */

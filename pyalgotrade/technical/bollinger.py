# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import dataseries
from pyalgotrade.technical import ma
from pyalgotrade.technical import stats


class BollingerBands(object):
    """Bollinger Bands filter as described in http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:bollinger_bands.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use in the calculation. Must be > 1.
    :type period: int.
    :param numStdDev: The number of standard deviations to use for the upper and lower bands.
    :type numStdDev: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, numStdDev, maxLen=None):
        self.__sma = ma.SMA(dataSeries, period, maxLen=maxLen)
        self.__stdDev = stats.StdDev(dataSeries, period, maxLen=maxLen)
        self.__upperBand = dataseries.SequenceDataSeries(maxLen)
        self.__lowerBand = dataseries.SequenceDataSeries(maxLen)
        self.__numStdDev = numStdDev
        self.__bandWidth = dataseries.SequenceDataSeries(maxLen)
        # It is important to subscribe after sma and stddev since we'll use those values.
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def partialInitiate(self, dataSeries, period, numStdDev, maxLen=None):
        self.__sma = ma.SMA_AddBarVersion(dataSeries, period, maxLen=maxLen)
        self.__stdDev = stats.StdDev_AddBarVersion(dataSeries, period, maxLen=maxLen)
        self.__upperBand = dataseries.SequenceDataSeries(maxLen)
        self.__lowerBand = dataseries.SequenceDataSeries(maxLen)
        self.__numStdDev = numStdDev
        self.__bandWidth = dataseries.SequenceDataSeries(maxLen)
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)
    
    def __onNewValue(self, dataSeries, dateTime, value):
        upperValue = None
        lowerValue = None
        bandWidth = None

        if value is not None:
            sma = self.__sma[-1]
            if sma is not None:
                stdDev = self.__stdDev[-1]
                upperValue = sma + stdDev * self.__numStdDev
                lowerValue = sma + stdDev * self.__numStdDev * -1
                bandWidth = stdDev / sma

        self.__upperBand.appendWithDateTime(dateTime, upperValue)
        self.__lowerBand.appendWithDateTime(dateTime, lowerValue)
        self.__bandWidth.appendWithDateTime(dateTime, bandWidth)
        
    def getStdDev(self):
        """
        Returns the stdDev as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__stdDev
            
    def getUpperBand(self):
        """
        Returns the upper band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__upperBand

    def getMiddleBand(self):
        """
        Returns the middle band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__sma

    def getLowerBand(self):
        """
        Returns the lower band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__lowerBand
    
    def getBandWidth(self):
        """
        Returns the band width as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__bandWidth
    
    def setSMA(self, sma):
        self.__sma = sma
        
    def setStdDev(self, stdDev):
        self.__stdDev = stdDev

class BollingerBands_AddBarVersion(BollingerBands):
    def __init__(self, dataSeries, period, numStdDev, maxLen=None):
        #super(BollingerBands_AddBarVersion,self).__init__(dataSeries, period, numStdDev, maxLen)
        #super(BollingerBands_AddBarVersion, self).setSMA(ma.SMA_AddBarVersion(dataSeries, period, maxLen=maxLen))
        #super(BollingerBands_AddBarVersion, self).setStdDev(stats.StdDev_AddBarVersion(dataSeries, period, maxLen=maxLen))
        self.partialInitiate(dataSeries, period, numStdDev, maxLen)
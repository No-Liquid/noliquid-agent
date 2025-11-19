ta.alma()2 overloads

Arnaud Legoux Moving Average. It uses Gaussian distribution as weights for moving average.
SYNTAX & OVERLOADS
ta.alma(series, length, offset, sigma) → series float
ta.alma(series, length, offset, sigma, floor) → series float
ARGUMENTS
series (series int/float) Series of values to process.
length (series int) Number of bars (length).
offset (simple int/float) Controls tradeoff between smoothness (closer to 1) and responsiveness (closer to 0).
sigma (simple int/float) Changes the smoothness of ALMA. The larger sigma the smoother ALMA.
EXAMPLE

//@version=5
indicator("ta.alma", overlay=true) 
plot(ta.alma(close, 9, 0.85, 6))

// same on pine, but much less efficient
pine_alma(series, windowsize, offset, sigma) =>
    m = offset * (windowsize - 1)
    //m = math.floor(offset * (windowsize - 1)) // Used as m when math.floor=true
    s = windowsize / sigma
    norm = 0.0
    sum = 0.0
    for i = 0 to windowsize - 1
        weight = math.exp(-1 * math.pow(i - m, 2) / (2 * math.pow(s, 2)))
        norm := norm + weight
        sum := sum + series[windowsize - i - 1] * weight
    sum / norm
plot(pine_alma(close, 9, 0.85, 6))
RETURNS
Arnaud Legoux Moving Average.
REMARKS
na values in the source series are included in calculations and will produce an na result.
SEE ALSO
ta.sma
ta.ema
ta.rma
ta.wma
ta.vwma
ta.swma
ta.atr()

Function atr (average true range) returns the RMA of true range. True range is max(high - low, abs(high - close[1]), abs(low - close[1])).
SYNTAX
ta.atr(length) → series float
ARGUMENTS
length (simple int) Length (number of bars back).
EXAMPLE

//@version=5
indicator("ta.atr")
plot(ta.atr(14))

//the same on pine
pine_atr(length) =>
    trueRange = na(high[1])? high-low : math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))
    //true range can be also calculated with ta.tr(true)
    ta.rma(trueRange, length)

plot(pine_atr(14))
RETURNS
Average true range.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.tr
ta.rma
ta.barssince()

Counts the number of bars since the last time the condition was true.
SYNTAX
ta.barssince(condition) → series int
ARGUMENTS
condition (series bool) The condition to check for.
EXAMPLE

//@version=5
indicator("ta.barssince")
// get number of bars since last color.green bar
plot(ta.barssince(close >= open))
RETURNS
Number of bars since condition was true.
REMARKS
If the condition has never been met prior to the current bar, the function returns na.
Please note that using this variable/function can cause indicator repainting.
SEE ALSO
ta.lowestbars
ta.highestbars
ta.valuewhen
ta.highest
ta.lowest
ta.bb()

Bollinger Bands. A Bollinger Band is a technical analysis tool defined by a set of lines plotted two standard deviations (positively and negatively) away from a simple moving average (SMA) of the security's price, but can be adjusted to user preferences.
SYNTAX
ta.bb(series, length, mult) → [series float, series float, series float]
ARGUMENTS
series (series int/float) Series of values to process.
length (series int) Number of bars (length).
mult (simple int/float) Standard deviation factor.
EXAMPLE

//@version=5
indicator("ta.bb")

[middle, upper, lower] = ta.bb(close, 5, 4)
plot(middle, color=color.yellow)
plot(upper, color=color.yellow)
plot(lower, color=color.yellow)

// the same on pine
f_bb(src, length, mult) =>
    float basis = ta.sma(src, length)
    float dev = mult * ta.stdev(src, length)
    [basis, basis + dev, basis - dev]

[pineMiddle, pineUpper, pineLower] = f_bb(close, 5, 4)

plot(pineMiddle)
plot(pineUpper)
plot(pineLower)
RETURNS
Bollinger Bands.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.sma
ta.stdev
ta.kc
ta.bbw()

Bollinger Bands Width. The Bollinger Band Width is the difference between the upper and the lower Bollinger Bands divided by the middle band.
SYNTAX
ta.bbw(series, length, mult) → series float
ARGUMENTS
series (series int/float) Series of values to process.
length (series int) Number of bars (length).
mult (simple int/float) Standard deviation factor.
EXAMPLE

//@version=5
indicator("ta.bbw")

plot(ta.bbw(close, 5, 4), color=color.yellow)

// the same on pine
f_bbw(src, length, mult) =>
    float basis = ta.sma(src, length)
    float dev = mult * ta.stdev(src, length)
    ((basis + dev) - (basis - dev)) / basis

plot(f_bbw(close, 5, 4))
RETURNS
Bollinger Bands Width.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.bb
ta.sma
ta.stdev
ta.cci()

The CCI (commodity channel index) is calculated as the difference between the typical price of a commodity and its simple moving average, divided by the mean absolute deviation of the typical price. The index is scaled by an inverse factor of 0.015 to provide more readable numbers.
SYNTAX
ta.cci(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
RETURNS
Commodity channel index of source for length bars back.
REMARKS
na values in the source series are ignored.
ta.change()6 overloads

Compares the current source value to its value length bars ago and returns the difference.
SYNTAX & OVERLOADS
ta.change(source) → series int
ta.change(source) → series float
ta.change(source, length) → series int
ta.change(source, length) → series float
ta.change(source) → series bool
ta.change(source, length) → series bool
ARGUMENTS
source (series int) Source series.
EXAMPLE

//@version=5
indicator('Day and Direction Change', overlay = true)
dailyBarTime = time('1D')
isNewDay = ta.change(dailyBarTime) != 0
bgcolor(isNewDay ? color.new(color.green, 80) : na)

isGreenBar = close >= open
colorChange = ta.change(isGreenBar)
plotshape(colorChange, 'Direction Change')
RETURNS
The difference between the values when they are numerical. When a 'bool' source is used, returns true when the current source is different from the previous source.
REMARKS
na values in the source series are included in calculations and will produce an na result.
SEE ALSO
ta.mom
ta.cross
ta.cmo()

Chande Momentum Oscillator. Calculates the difference between the sum of recent gains and the sum of recent losses and then divides the result by the sum of all price movement over the same period.
SYNTAX
ta.cmo(series, length) → series float
ARGUMENTS
series (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.cmo")
plot(ta.cmo(close, 5), color=color.yellow)

// the same on pine
f_cmo(src, length) =>
    float mom = ta.change(src)
    float sm1 = math.sum((mom >= 0) ? mom : 0.0, length)
    float sm2 = math.sum((mom >= 0) ? 0.0 : -mom, length)
    100 * (sm1 - sm2) / (sm1 + sm2)

plot(f_cmo(close, 5))
RETURNS
Chande Momentum Oscillator.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.rsi
ta.stoch
math.sum
ta.cog()

The cog (center of gravity) is an indicator based on statistics and the Fibonacci golden ratio.
SYNTAX
ta.cog(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.cog", overlay=true) 
plot(ta.cog(close, 10))

// the same on pine
pine_cog(source, length) =>
    sum = math.sum(source, length)
    num = 0.0
    for i = 0 to length - 1
        price = source[i]
        num := num + price * (i + 1)
    -num / sum

plot(pine_cog(close, 10))
RETURNS
Center of Gravity.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.stoch
ta.correlation()

Correlation coefficient. Describes the degree to which two series tend to deviate from their ta.sma values.
SYNTAX
ta.correlation(source1, source2, length) → series float
ARGUMENTS
source1 (series int/float) Source series.
source2 (series int/float) Target series.
length (series int) Length (number of bars back).
RETURNS
Correlation coefficient.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
request.security
ta.cross()

SYNTAX
ta.cross(source1, source2) → series bool
ARGUMENTS
source1 (series int/float) First data series.
source2 (series int/float) Second data series.
RETURNS
true if two series have crossed each other, otherwise false.
SEE ALSO
ta.change
ta.crossover()

The source1-series is defined as having crossed over source2-series if, on the current bar, the value of source1 is greater than the value of source2, and on the previous bar, the value of source1 was less than or equal to the value of source2.
SYNTAX
ta.crossover(source1, source2) → series bool
ARGUMENTS
source1 (series int/float) First data series.
source2 (series int/float) Second data series.
RETURNS
true if source1 crossed over source2 otherwise false.
ta.crossunder()

The source1-series is defined as having crossed under source2-series if, on the current bar, the value of source1 is less than the value of source2, and on the previous bar, the value of source1 was greater than or equal to the value of source2.
SYNTAX
ta.crossunder(source1, source2) → series bool
ARGUMENTS
source1 (series int/float) First data series.
source2 (series int/float) Second data series.
RETURNS
true if source1 crossed under source2 otherwise false.
ta.cum()

Cumulative (total) sum of source. In other words it's a sum of all elements of source.
SYNTAX
ta.cum(source) → series float
ARGUMENTS
source (series int/float) Source used for the calculation.
RETURNS
Total sum series.
SEE ALSO
math.sum
ta.dev()

Measure of difference between the series and it's ta.sma
SYNTAX
ta.dev(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.dev")
plot(ta.dev(close, 10))

// the same on pine
pine_dev(source, length) =>
    mean = ta.sma(source, length)
    sum = 0.0
    for i = 0 to length - 1
        val = source[i]
        sum := sum + math.abs(val - mean)
    dev = sum/length
plot(pine_dev(close, 10))
RETURNS
Deviation of source for length bars back.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.variance
ta.stdev
ta.dmi()

The dmi function returns the directional movement index.
SYNTAX
ta.dmi(diLength, adxSmoothing) → [series float, series float, series float]
ARGUMENTS
diLength (simple int) DI Period.
adxSmoothing (simple int) ADX Smoothing Period.
EXAMPLE

//@version=5
indicator(title="Directional Movement Index", shorttitle="DMI", format=format.price, precision=4)
len = input.int(17, minval=1, title="DI Length")
lensig = input.int(14, title="ADX Smoothing", minval=1)
[diplus, diminus, adx] = ta.dmi(len, lensig)
plot(adx, color=color.red, title="ADX")
plot(diplus, color=color.blue, title="+DI")
plot(diminus, color=color.orange, title="-DI")
RETURNS
Tuple of three DMI series: Positive Directional Movement (+DI), Negative Directional Movement (-DI) and Average Directional Movement Index (ADX).
SEE ALSO
ta.rsi
ta.tsi
ta.mfi
ta.ema()

The ema function returns the exponentially weighted moving average. In ema weighting factors decrease exponentially. It calculates by using a formula: EMA = alpha * source + (1 - alpha) * EMA[1], where alpha = 2 / (length + 1).
SYNTAX
ta.ema(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (simple int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.ema")
plot(ta.ema(close, 15))

//the same on pine
pine_ema(src, length) =>
    alpha = 2 / (length + 1)
    sum = 0.0
    sum := na(sum[1]) ? src : alpha * src + (1 - alpha) * nz(sum[1])
plot(pine_ema(close,15))
RETURNS
Exponential moving average of source with alpha = 2 / (length + 1).
REMARKS
Please note that using this variable/function can cause indicator repainting.
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.sma
ta.rma
ta.wma
ta.vwma
ta.swma
ta.alma
ta.falling()

Test if the source series is now falling for length bars long.
SYNTAX
ta.falling(source, length) → series bool
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
RETURNS
true if current source value is less than any previous source value for length bars back, false otherwise.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.rising
ta.highest()2 overloads

Highest value for a given number of bars back.
SYNTAX & OVERLOADS
ta.highest(length) → series float
ta.highest(source, length) → series float
ARGUMENTS
length (series int) Number of bars (length).
RETURNS
Highest value in the series.
REMARKS
Two args version: source is a series and length is the number of bars back.
One arg version: length is the number of bars back. Algorithm uses high as a source series.
na values in the source series are ignored.
SEE ALSO
ta.lowest
ta.lowestbars
ta.highestbars
ta.valuewhen
ta.barssince
ta.highestbars()2 overloads

Highest value offset for a given number of bars back.
SYNTAX & OVERLOADS
ta.highestbars(length) → series int
ta.highestbars(source, length) → series int
ARGUMENTS
length (series int) Number of bars (length).
RETURNS
Offset to the highest bar.
REMARKS
Two args version: source is a series and length is the number of bars back.
One arg version: length is the number of bars back. Algorithm uses high as a source series.
na values in the source series are ignored.
SEE ALSO
ta.lowest
ta.highest
ta.lowestbars
ta.barssince
ta.valuewhen
ta.hma()

The hma function returns the Hull Moving Average.
SYNTAX
ta.hma(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (simple int) Number of bars.
EXAMPLE

//@version=5
indicator("Hull Moving Average")
src = input(defval=close, title="Source")
length = input(defval=9, title="Length")
hmaBuildIn = ta.hma(src, length)
plot(hmaBuildIn, title="Hull MA", color=#674EA7)
RETURNS
Hull moving average of 'source' for 'length' bars back.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.ema
ta.rma
ta.wma
ta.vwma
ta.sma
ta.kc()2 overloads

Keltner Channels. Keltner channel is a technical analysis indicator showing a central moving average line plus channel lines at a distance above and below.
SYNTAX & OVERLOADS
ta.kc(series, length, mult) → [series float, series float, series float]
ta.kc(series, length, mult, useTrueRange) → [series float, series float, series float]
ARGUMENTS
series (series int/float) Series of values to process.
length (simple int) Number of bars (length).
mult (simple int/float) Standard deviation factor.
EXAMPLE

//@version=5
indicator("ta.kc")

[middle, upper, lower] = ta.kc(close, 5, 4)
plot(middle, color=color.yellow)
plot(upper, color=color.yellow)
plot(lower, color=color.yellow)


// the same on pine
f_kc(src, length, mult, useTrueRange) =>
    float basis = ta.ema(src, length)
    float span = (useTrueRange) ? ta.tr : (high - low)
    float rangeEma = ta.ema(span, length)
    [basis, basis + rangeEma * mult, basis - rangeEma * mult]
    
[pineMiddle, pineUpper, pineLower] = f_kc(close, 5, 4, true)

plot(pineMiddle)
plot(pineUpper)
plot(pineLower)
RETURNS
Keltner Channels.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.ema
ta.atr
ta.bb
ta.kcw()2 overloads

Keltner Channels Width. The Keltner Channels Width is the difference between the upper and the lower Keltner Channels divided by the middle channel.
SYNTAX & OVERLOADS
ta.kcw(series, length, mult) → series float
ta.kcw(series, length, mult, useTrueRange) → series float
ARGUMENTS
series (series int/float) Series of values to process.
length (simple int) Number of bars (length).
mult (simple int/float) Standard deviation factor.
EXAMPLE

//@version=5
indicator("ta.kcw")

plot(ta.kcw(close, 5, 4), color=color.yellow)

// the same on pine
f_kcw(src, length, mult, useTrueRange) =>
    float basis = ta.ema(src, length)
    float span = (useTrueRange) ? ta.tr : (high - low)
    float rangeEma = ta.ema(span, length)
    
    ((basis + rangeEma * mult) - (basis - rangeEma * mult)) / basis

plot(f_kcw(close, 5, 4, true))
RETURNS
Keltner Channels Width.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.kc
ta.ema
ta.atr
ta.bb
ta.linreg()

Linear regression curve. A line that best fits the prices specified over a user-defined time period. It is calculated using the least squares method. The result of this function is calculated using the formula: linreg = intercept + slope * (length - 1 - offset), where intercept and slope are the values calculated with the least squares method on source series.
SYNTAX
ta.linreg(source, length, offset) → series float
ARGUMENTS
source (series int/float) Source series.
length (series int) Number of bars (length).
offset (simple int) Offset.
RETURNS
Linear regression curve.
REMARKS
na values in the source series are included in calculations and will produce an na result.
ta.lowest()2 overloads

Lowest value for a given number of bars back.
SYNTAX & OVERLOADS
ta.lowest(length) → series float
ta.lowest(source, length) → series float
ARGUMENTS
length (series int) Number of bars (length).
RETURNS
Lowest value in the series.
REMARKS
Two args version: source is a series and length is the number of bars back.
One arg version: length is the number of bars back. Algorithm uses low as a source series.
na values in the source series are ignored.
SEE ALSO
ta.highest
ta.lowestbars
ta.highestbars
ta.valuewhen
ta.barssince
ta.lowestbars()2 overloads

Lowest value offset for a given number of bars back.
SYNTAX & OVERLOADS
ta.lowestbars(length) → series int
ta.lowestbars(source, length) → series int
ARGUMENTS
length (series int) Number of bars back.
RETURNS
Offset to the lowest bar.
REMARKS
Two args version: source is a series and length is the number of bars back.
One arg version: length is the number of bars back. Algorithm uses low as a source series.
na values in the source series are ignored.
SEE ALSO
ta.lowest
ta.highest
ta.highestbars
ta.barssince
ta.valuewhen
ta.macd()

MACD (moving average convergence/divergence). It is supposed to reveal changes in the strength, direction, momentum, and duration of a trend in a stock's price.
SYNTAX
ta.macd(source, fastlen, slowlen, siglen) → [series float, series float, series float]
ARGUMENTS
source (series int/float) Series of values to process.
fastlen (simple int) Fast Length parameter.
slowlen (simple int) Slow Length parameter.
siglen (simple int) Signal Length parameter.
EXAMPLE

//@version=5
indicator("MACD")
[macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)
plot(macdLine, color=color.blue)
plot(signalLine, color=color.orange)
plot(histLine, color=color.red, style=plot.style_histogram)
If you need only one value, use placeholders '_' like this:
EXAMPLE

//@version=5
indicator("MACD")
[_, signalLine, _] = ta.macd(close, 12, 26, 9)
plot(signalLine, color=color.orange)
RETURNS
Tuple of three MACD series: MACD line, signal line and histogram line.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.sma
ta.ema
ta.max()

Returns the all-time high value of source from the beginning of the chart up to the current bar.
SYNTAX
ta.max(source) → series float
ARGUMENTS
source (series int/float) Source used for the calculation.
REMARKS
na occurrences of source are ignored.
ta.median()2 overloads

Returns the median of the series.
SYNTAX & OVERLOADS
ta.median(source, length) → series int
ta.median(source, length) → series float
ARGUMENTS
source (series int) Series of values to process.
length (series int) Number of bars (length).
RETURNS
The median of the series.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
ta.mfi()

Money Flow Index. The Money Flow Index (MFI) is a technical oscillator that uses price and volume for identifying overbought or oversold conditions in an asset.
SYNTAX
ta.mfi(series, length) → series float
ARGUMENTS
series (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("Money Flow Index")

plot(ta.mfi(hlc3, 14), color=color.yellow)

// the same on pine
pine_mfi(src, length) =>
    float upper = math.sum(volume * (ta.change(src) <= 0.0 ? 0.0 : src), length)
    float lower = math.sum(volume * (ta.change(src) >= 0.0 ? 0.0 : src), length)
    mfi = 100.0 - (100.0 / (1.0 + upper / lower))
    mfi

plot(pine_mfi(hlc3, 14))
RETURNS
Money Flow Index.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.rsi
math.sum
ta.min()

Returns the all-time low value of source from the beginning of the chart up to the current bar.
SYNTAX
ta.min(source) → series float
ARGUMENTS
source (series int/float) Source used for the calculation.
REMARKS
na occurrences of source are ignored.
ta.mode()2 overloads

Returns the mode of the series. If there are several values with the same frequency, it returns the smallest value.
SYNTAX & OVERLOADS
ta.mode(source, length) → series int
ta.mode(source, length) → series float
ARGUMENTS
source (series int) Series of values to process.
length (series int) Number of bars (length).
RETURNS
The most frequently occurring value from the source. If none exists, returns the smallest value instead.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
ta.mom()

Momentum of source price and source price length bars ago. This is simply a difference: source - source[length].
SYNTAX
ta.mom(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Offset from the current bar to the previous bar.
RETURNS
Momentum of source price and source price length bars ago.
REMARKS
na values in the source series are included in calculations and will produce an na result.
SEE ALSO
ta.change
ta.percentile_linear_interpolation()

Calculates percentile using method of linear interpolation between the two nearest ranks.
SYNTAX
ta.percentile_linear_interpolation(source, length, percentage) → series float
ARGUMENTS
source (series int/float) Series of values to process (source).
length (series int) Number of bars back (length).
percentage (simple int/float) Percentage, a number from range 0..100.
RETURNS
P-th percentile of source series for length bars back.
REMARKS
Note that a percentile calculated using this method will NOT always be a member of the input data set.
na values in the source series are included in calculations and will produce an na result.
SEE ALSO
ta.percentile_nearest_rank
ta.percentile_nearest_rank()

Calculates percentile using method of Nearest Rank.
SYNTAX
ta.percentile_nearest_rank(source, length, percentage) → series float
ARGUMENTS
source (series int/float) Series of values to process (source).
length (series int) Number of bars back (length).
percentage (simple int/float) Percentage, a number from range 0..100.
RETURNS
P-th percentile of source series for length bars back.
REMARKS
Using the Nearest Rank method on lengths less than 100 bars back can result in the same number being used for more than one percentile.
A percentile calculated using the Nearest Rank method will always be a member of the input data set.
The 100th percentile is defined to be the largest value in the input data set.
na values in the source series are ignored.
SEE ALSO
ta.percentile_linear_interpolation
ta.percentrank()

Percent rank is the percents of how many previous values was less than or equal to the current value of given series.
SYNTAX
ta.percentrank(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
RETURNS
Percent rank of source for length bars back.
REMARKS
na values in the source series are included in calculations and will produce an na result.
ta.pivot_point_levels()

Calculates the pivot point levels using the specified type and anchor.
SYNTAX
ta.pivot_point_levels(type, anchor, developing) → array<float>
ARGUMENTS
type (series string) The type of pivot point levels. Possible values: "Traditional", "Fibonacci", "Woodie", "Classic", "DM", "Camarilla".
anchor (series bool) The condition that triggers the reset of the pivot point calculations. When true, calculations reset; when false, results calculated at the last reset persist.
developing (series bool) If false, the values are those calculated the last time the anchor condition was true. They remain constant until the anchor condition becomes true again. If true, the pivots are developing, i.e., they constantly recalculate on the data developing between the point of the last anchor (or bar zero if the anchor condition was never true) and the current bar. Optional. The default is false.
EXAMPLE

//@version=5
indicator("Weekly Pivots", max_lines_count=500, overlay=true)
timeframe = "1W"
typeInput = input.string("Traditional", "Type", options=["Traditional", "Fibonacci", "Woodie", "Classic", "DM", "Camarilla"])
weekChange = timeframe.change(timeframe)
pivotPointsArray = ta.pivot_point_levels(typeInput, weekChange)
if weekChange
    for pivotLevel in pivotPointsArray
        line.new(time, pivotLevel, time + timeframe.in_seconds(timeframe) * 1000, pivotLevel, xloc=xloc.bar_time)
RETURNS
An array<float> with numerical values representing 11 pivot point levels: [P, R1, S1, R2, S2, R3, S3, R4, S4, R5, S5]. Levels absent from the specified type return na values (e.g., "DM" only calculates P, R1, and S1).
REMARKS
The developing parameter cannot be true when type is set to "Woodie", because the Woodie calculation for a period depends on that period's open, which means that the pivot value is either available or unavailable, but never developing. If used together, the indicator will return a runtime error.
ta.pivothigh()2 overloads

This function returns price of the pivot high point. It returns 'NaN', if there was no pivot high point.
SYNTAX & OVERLOADS
ta.pivothigh(leftbars, rightbars) → series float
ta.pivothigh(source, leftbars, rightbars) → series float
ARGUMENTS
leftbars (series int/float) Left strength.
rightbars (series int/float) Right strength.
EXAMPLE

//@version=5
indicator("PivotHigh", overlay=true)
leftBars = input(2)
rightBars=input(2)
ph = ta.pivothigh(leftBars, rightBars)
plot(ph, style=plot.style_cross, linewidth=3, color= color.red, offset=-rightBars)
RETURNS
Price of the point or 'NaN'.
REMARKS
If parameters 'leftbars' or 'rightbars' are series you should use max_bars_back function for the 'source' variable.
ta.pivotlow()2 overloads

This function returns price of the pivot low point. It returns 'NaN', if there was no pivot low point.
SYNTAX & OVERLOADS
ta.pivotlow(leftbars, rightbars) → series float
ta.pivotlow(source, leftbars, rightbars) → series float
ARGUMENTS
leftbars (series int/float) Left strength.
rightbars (series int/float) Right strength.
EXAMPLE

//@version=5
indicator("PivotLow", overlay=true)
leftBars = input(2)
rightBars=input(2)
pl = ta.pivotlow(close, leftBars, rightBars)
plot(pl, style=plot.style_cross, linewidth=3, color= color.blue, offset=-rightBars)
RETURNS
Price of the point or 'NaN'.
REMARKS
If parameters 'leftbars' or 'rightbars' are series you should use max_bars_back function for the 'source' variable.
ta.range()2 overloads

Returns the difference between the min and max values in a series.
SYNTAX & OVERLOADS
ta.range(source, length) → series int
ta.range(source, length) → series float
ARGUMENTS
source (series int) Series of values to process.
length (series int) Number of bars (length).
RETURNS
The difference between the min and max values in the series.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
ta.rising()

Test if the source series is now rising for length bars long.
SYNTAX
ta.rising(source, length) → series bool
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
RETURNS
true if current source is greater than any previous source for length bars back, false otherwise.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.falling
ta.rma()

Moving average used in RSI. It is the exponentially weighted moving average with alpha = 1 / length.
SYNTAX
ta.rma(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (simple int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.rma")
plot(ta.rma(close, 15))

//the same on pine
pine_rma(src, length) =>
    alpha = 1/length
    sum = 0.0
    sum := na(sum[1]) ? ta.sma(src, length) : alpha * src + (1 - alpha) * nz(sum[1])
plot(pine_rma(close, 15))
RETURNS
Exponential moving average of source with alpha = 1 / length.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.sma
ta.ema
ta.wma
ta.vwma
ta.swma
ta.alma
ta.rsi
ta.roc()

Calculates the percentage of change (rate of change) between the current value of source and its value length bars ago.
It is calculated by the formula: 100 * change(src, length) / src[length].
SYNTAX
ta.roc(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
RETURNS
The rate of change of source for length bars back.
REMARKS
na values in the source series are included in calculations and will produce an na result.
ta.rsi()

Relative strength index. It is calculated using the ta.rma() of upward and downward changes of source over the last length bars.
SYNTAX
ta.rsi(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (simple int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.rsi")
plot(ta.rsi(close, 7))

// same on pine, but less efficient
pine_rsi(x, y) => 
    u = math.max(x - x[1], 0) // upward ta.change
    d = math.max(x[1] - x, 0) // downward ta.change
    rs = ta.rma(u, y) / ta.rma(d, y)
    res = 100 - 100 / (1 + rs)
    res

plot(pine_rsi(close, 7))
RETURNS
Relative strength index.
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.rma
ta.sar()

Parabolic SAR (parabolic stop and reverse) is a method devised by J. Welles Wilder, Jr., to find potential reversals in the market price direction of traded goods.
SYNTAX
ta.sar(start, inc, max) → series float
ARGUMENTS
start (simple int/float) Start.
inc (simple int/float) Increment.
max (simple int/float) Maximum.
EXAMPLE

//@version=5
indicator("ta.sar")
plot(ta.sar(0.02, 0.02, 0.2), style=plot.style_cross, linewidth=3)

// The same on Pine Script®
pine_sar(start, inc, max) =>
    var float result = na
    var float maxMin = na
    var float acceleration = na
    var bool isBelow = na
    bool isFirstTrendBar = false
    
    if bar_index == 1
        if close > close[1]
            isBelow := true
            maxMin := high
            result := low[1]
        else
            isBelow := false
            maxMin := low
            result := high[1]
        isFirstTrendBar := true
        acceleration := start
    
    result := result + acceleration * (maxMin - result)
    
    if isBelow
        if result > low
            isFirstTrendBar := true
            isBelow := false
            result := math.max(high, maxMin)
            maxMin := low
            acceleration := start
    else
        if result < high
            isFirstTrendBar := true
            isBelow := true
            result := math.min(low, maxMin)
            maxMin := high
            acceleration := start
            
    if not isFirstTrendBar
        if isBelow
            if high > maxMin
                maxMin := high
                acceleration := math.min(acceleration + inc, max)
        else
            if low < maxMin
                maxMin := low
                acceleration := math.min(acceleration + inc, max)
    
    if isBelow
        result := math.min(result, low[1])
        if bar_index > 1
            result := math.min(result, low[2])
        
    else
        result := math.max(result, high[1])
        if bar_index > 1
            result := math.max(result, high[2])
    
    result
    
plot(pine_sar(0.02, 0.02, 0.2), style=plot.style_cross, linewidth=3)
RETURNS
Parabolic SAR.
ta.sma()

The sma function returns the moving average, that is the sum of last y values of x, divided by y.
SYNTAX
ta.sma(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.sma")
plot(ta.sma(close, 15))

// same on pine, but much less efficient
pine_sma(x, y) =>
    sum = 0.0
    for i = 0 to y - 1
        sum := sum + x[i] / y
    sum
plot(pine_sma(close, 15))
RETURNS
Simple moving average of source for length bars back.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.ema
ta.rma
ta.wma
ta.vwma
ta.swma
ta.alma
ta.stdev()

SYNTAX
ta.stdev(source, length, biased) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
biased (series bool) Determines which estimate should be used. Optional. The default is true.
EXAMPLE

//@version=5
indicator("ta.stdev")
plot(ta.stdev(close, 5))

//the same on pine
isZero(val, eps) => math.abs(val) <= eps

SUM(fst, snd) =>
    EPS = 1e-10
    res = fst + snd
    if isZero(res, EPS)
        res := 0
    else
        if not isZero(res, 1e-4)
            res := res
        else
            15

pine_stdev(src, length) =>
    avg = ta.sma(src, length)
    sumOfSquareDeviations = 0.0
    for i = 0 to length - 1
        sum = SUM(src[i], -avg)
        sumOfSquareDeviations := sumOfSquareDeviations + sum * sum

    stdev = math.sqrt(sumOfSquareDeviations / length)
plot(pine_stdev(close, 5))
RETURNS
Standard deviation.
REMARKS
If biased is true, function will calculate using a biased estimate of the entire population, if false - unbiased estimate of a sample.
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.dev
ta.variance
ta.stoch()

Stochastic. It is calculated by a formula: 100 * (close - lowest(low, length)) / (highest(high, length) - lowest(low, length)).
SYNTAX
ta.stoch(source, high, low, length) → series float
ARGUMENTS
source (series int/float) Source series.
high (series int/float) Series of high.
low (series int/float) Series of low.
length (series int) Length (number of bars back).
RETURNS
Stochastic.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.cog
ta.supertrend()

The Supertrend Indicator. The Supertrend is a trend following indicator.
SYNTAX
ta.supertrend(factor, atrPeriod) → [series float, series float]
ARGUMENTS
factor (series int/float) The multiplier by which the ATR will get multiplied.
atrPeriod (simple int) Length of ATR.
EXAMPLE

//@version=5
indicator("Pine Script® Supertrend")

[supertrend, direction] = ta.supertrend(3, 10)
plot(direction < 0 ? supertrend : na, "Up direction", color = color.green, style=plot.style_linebr)
plot(direction > 0 ? supertrend : na, "Down direction", color = color.red, style=plot.style_linebr)

// The same on Pine Script®
pine_supertrend(factor, atrPeriod) =>
    src = hl2
    atr = ta.atr(atrPeriod)
    upperBand = src + factor * atr
    lowerBand = src - factor * atr
    prevLowerBand = nz(lowerBand[1])
    prevUpperBand = nz(upperBand[1])

    lowerBand := lowerBand > prevLowerBand or close[1] < prevLowerBand ? lowerBand : prevLowerBand
    upperBand := upperBand < prevUpperBand or close[1] > prevUpperBand ? upperBand : prevUpperBand
    int _direction = na
    float superTrend = na
    prevSuperTrend = superTrend[1]
    if na(atr[1])
        _direction := 1
    else if prevSuperTrend == prevUpperBand
        _direction := close > upperBand ? -1 : 1
    else
        _direction := close < lowerBand ? 1 : -1
    superTrend := _direction == -1 ? lowerBand : upperBand
    [superTrend, _direction]

[Pine_Supertrend, pineDirection] = pine_supertrend(3, 10)
plot(pineDirection < 0 ? Pine_Supertrend : na, "Up direction", color = color.green, style=plot.style_linebr)
plot(pineDirection > 0 ? Pine_Supertrend : na, "Down direction", color = color.red, style=plot.style_linebr)
RETURNS
Tuple of two supertrend series: supertrend line and direction of trend. Possible values are 1 (down direction) and -1 (up direction).
SEE ALSO
ta.macd
ta.swma()

Symmetrically weighted moving average with fixed length: 4. Weights: [1/6, 2/6, 2/6, 1/6].
SYNTAX
ta.swma(source) → series float
ARGUMENTS
source (series int/float) Source series.
EXAMPLE

//@version=5
indicator("ta.swma")
plot(ta.swma(close))

// same on pine, but less efficient
pine_swma(x) =>
    x[3] * 1 / 6 + x[2] * 2 / 6 + x[1] * 2 / 6 + x[0] * 1 / 6
plot(pine_swma(close))
RETURNS
Symmetrically weighted moving average.
REMARKS
na values in the source series are included in calculations and will produce an na result.
SEE ALSO
ta.sma
ta.ema
ta.rma
ta.wma
ta.vwma
ta.alma
ta.tr()

SYNTAX
ta.tr(handle_na) → series float
ARGUMENTS
handle_na (simple bool) How NaN values are handled. if true, and previous day's close is NaN then tr would be calculated as current day high-low. Otherwise (if false) tr would return NaN in such cases. Also note, that ta.atr uses ta.tr(true).
RETURNS
True range. It is math.max(high - low, math.abs(high - close[1]), math.abs(low - close[1])).
REMARKS
ta.tr(false) is exactly the same as ta.tr.
SEE ALSO
ta.tr
ta.atr
ta.tsi()

True strength index. It uses moving averages of the underlying momentum of a financial instrument.
SYNTAX
ta.tsi(source, short_length, long_length) → series float
ARGUMENTS
source (series int/float) Source series.
short_length (simple int) Short length.
long_length (simple int) Long length.
RETURNS
True strength index. A value in range [-1, 1].
REMARKS
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
ta.valuewhen()4 overloads

Returns the value of the source series on the bar where the condition was true on the nth most recent occurrence.
SYNTAX & OVERLOADS
ta.valuewhen(condition, source, occurrence) → series color
ta.valuewhen(condition, source, occurrence) → series int
ta.valuewhen(condition, source, occurrence) → series float
ta.valuewhen(condition, source, occurrence) → series bool
ARGUMENTS
condition (series bool) The condition to search for.
source (series color) The value to be returned from the bar where the condition is met.
occurrence (simple int) The occurrence of the condition. The numbering starts from 0 and goes back in time, so '0' is the most recent occurrence of condition, '1' is the second most recent and so forth. Must be an integer >= 0.
EXAMPLE

//@version=5
indicator("ta.valuewhen")
slow = ta.sma(close, 7)
fast = ta.sma(close, 14)
// Get value of `close` on second most recent cross
plot(ta.valuewhen(ta.cross(slow, fast), close, 1))
REMARKS
This function requires execution on every bar. It is not recommended to use it inside a for or while loop structure, where its behavior can be unexpected. Please note that using this function can cause indicator repainting.
SEE ALSO
ta.lowestbars
ta.highestbars
ta.barssince
ta.highest
ta.lowest
ta.variance()

Variance is the expectation of the squared deviation of a series from its mean (ta.sma), and it informally measures how far a set of numbers are spread out from their mean.
SYNTAX
ta.variance(source, length, biased) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
biased (series bool) Determines which estimate should be used. Optional. The default is true.
RETURNS
Variance of source for length bars back.
REMARKS
If biased is true, function will calculate using a biased estimate of the entire population, if false - unbiased estimate of a sample.
na values in the source series are ignored; the function calculates on the length quantity of non-na values.
SEE ALSO
ta.dev
ta.stdev
ta.vwap()3 overloads

Volume weighted average price.
SYNTAX & OVERLOADS
ta.vwap(source) → series float
ta.vwap(source, anchor) → series float
ta.vwap(source, anchor, stdev_mult) → [series float, series float, series float]
ARGUMENTS
source (series int/float) Source used for the VWAP calculation.
EXAMPLE

//@version=5
indicator("Simple VWAP")
vwap = ta.vwap(open)
plot(vwap)
EXAMPLE

//@version=5
indicator("Advanced VWAP")
vwapAnchorInput = input.string("Daily", "Anchor", options = ["Daily", "Weekly", "Monthly"])
stdevMultiplierInput = input.float(1.0, "Standard Deviation Multiplier")
anchorTimeframe = switch vwapAnchorInput
    "Daily"   => "1D"
    "Weekly"  => "1W"
    "Monthly" => "1M"
anchor = timeframe.change(anchorTimeframe)
[vwap, upper, lower] = ta.vwap(open, anchor, stdevMultiplierInput)
plot(vwap)
plot(upper, color = color.green)
plot(lower, color = color.green)
RETURNS
A VWAP series, or a tuple [vwap, upper_band, lower_band] if stdev_mult is specified.
REMARKS
Calculations only begin the first time the anchor condition becomes true. Until then, the function returns na.
SEE ALSO
ta.vwap
ta.vwma()

The vwma function returns volume-weighted moving average of source for length bars back. It is the same as: sma(source * volume, length) / sma(volume, length).
SYNTAX
ta.vwma(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.vwma")
plot(ta.vwma(close, 15))

// same on pine, but less efficient
pine_vwma(x, y) =>
    ta.sma(x * volume, y) / ta.sma(volume, y)
plot(pine_vwma(close, 15))
RETURNS
Volume-weighted moving average of source for length bars back.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.sma
ta.ema
ta.rma
ta.wma
ta.swma
ta.alma
ta.wma()

The wma function returns weighted moving average of source for length bars back. In wma weighting factors decrease in arithmetical progression.
SYNTAX
ta.wma(source, length) → series float
ARGUMENTS
source (series int/float) Series of values to process.
length (series int) Number of bars (length).
EXAMPLE

//@version=5
indicator("ta.wma")
plot(ta.wma(close, 15))

// same on pine, but much less efficient
pine_wma(x, y) =>
    norm = 0.0
    sum = 0.0
    for i = 0 to y - 1
        weight = (y - i) * y
        norm := norm + weight
        sum := sum + x[i] * weight
    sum / norm
plot(pine_wma(close, 15))
RETURNS
Weighted moving average of source for length bars back.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.sma
ta.ema
ta.rma
ta.vwma
ta.swma
ta.alma
ta.wpr()

Williams %R. The oscillator shows the current closing price in relation to the high and low of the past 'length' bars.
SYNTAX
ta.wpr(length) → series float
ARGUMENTS
length (series int) Number of bars.
EXAMPLE

//@version=5
indicator("Williams %R", shorttitle="%R", format=format.price, precision=2)
plot(ta.wpr(14), title="%R", color=color.new(#ff6d00, 0))
RETURNS
Williams %R.
REMARKS
na values in the source series are ignored.
SEE ALSO
ta.mfi
ta.cmo
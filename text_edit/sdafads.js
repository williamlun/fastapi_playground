function Encode(fPort, obj, variables) {
    var convert = {
        // char is a single character, which is "0" in this encoding script
        // pad function here assumes padding from left
        pad: function (length, char, paddingString) {
            while (paddingString.length < length) {
                paddingString = char + paddingString
            }
            return paddingString
        },
    };

    if (fPort == 90) {
        var setTempHex = convert.pad(4, "0", (parseFloat(obj.setTemperature) * 10).toString(16));
        var fanModeHex = convert.pad(2, "0", parseFloat(obj.fanMode).toString(16));
        var thresholdHex = convert.pad(2, "0", parseFloat(obj.threshold).toString(16));
        var sysModeHex = convert.pad(2, "0", parseFloat(obj.systemState).toString(16));
        var coolPbandHex = convert.pad(2, "0", (parseFloat(obj.coolPband) * 10).toString(16));
        var coolItimeHex = convert.pad(4, "0", parseFloat(obj.coolItime).toString(16));
        var kFactorHex = convert.pad(2, "0", parseFloat(obj.kFactor).toString(16));
        var downLinkData = setTempHex + fanModeHex + thresholdHex + sysModeHex + coolPbandHex + coolItimeHex + kFactorHex;
        // var hexFinal = setTempHex.concat(fanModeHex, thresholdHex, sysModeHex, coolPbandHex, coolItimeHex, kFactorHex)
        // return Buffer.from(hexFinal).toString('base64');
        downlinkDataInt = downLinkData.match(/.{1,2}/g).map(function (byte) { return parseInt(byte, 16) });
        return downlinkDataInt;
    }

};

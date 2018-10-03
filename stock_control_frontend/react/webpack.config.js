const path = require("path");
const BundleTracker = require('webpack-bundle-tracker');
const statsFileURL = './webpack-stats.json';

module.exports = {

    context: __dirname,

    mode: 'development',

    devtool: 'inline-source-map',

    entry: `./assets/js/index.jsx`,

    output: {
        path: path.resolve(`./assets/bundles/`),
        filename: "[name]-[hash].js"
    },

    resolve: {
        extensions: [".jsx", ".js"]
    },

    plugins: [
        new BundleTracker({filename: statsFileURL}),
    ],

    module: {
        rules: [
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            }, {
                test: /\.jsx$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            {
                test: /\.(png|woff|woff2|eot|ttf|svg)$/,
                loader: 'url-loader?limit=100000'
            },
            {
                test: /\.css$/,
                loader: ['style-loader', 'css-loader'],
                //exclude: /node_modules/
            }

        ]
    }
};
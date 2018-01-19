import System.Environment
import Data.List
import Data.Time

data Entry = Entry { start :: UTCTime
                   , end :: UTCTime
                   , activity :: String
                   , project :: String
                   }

instance Show Entry where
    show (Entry a b c d) = concat [c, d] 

shortTime :: UTCTime -> String
shortTime = formatTime defaultTimeLocale "%y-%m-%d %H:%M:%S"

main = do
    start <- getCurrentTime
    args <- getArgs
    putStrLn $ shortTime start

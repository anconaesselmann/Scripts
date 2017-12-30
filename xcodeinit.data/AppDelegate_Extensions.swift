//  Created by Axel Ancona Esselmann on 12/16/17.
//  Copyright © 2017 Axel Ancona Esselmann. All rights reserved.
//

import UIKit

extension AppDelegate {
    func initWindow(with vc: UIViewController) {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = vc
        window?.makeKeyAndVisible()
    }
}

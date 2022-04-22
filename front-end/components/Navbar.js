import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars } from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
export default function Navbar({ primaryColor, secondaryColor, variant, title, links }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div>
      <nav
        className={`${primaryColor} flex px-4 sticky w-full shadow-sm z-10 py-3`}
      >
        <h1
          className={`${(variant == 'light') ? "text-white" : "text-black"} text-2xl mr-6 relative ${(variant == "light") ? "hover:text-gray-200" : "hover:text-gray-700"
          } font-bold`}
        >
          <Link href="/">
            <a>{title}</a>
          </Link>
        </h1>
        <div className="md:flex space-x-4 items-center hidden md:visible">
          {links.map((page, index) => {
            return (
              <Link key={index} href={page.address}>
                <a
                  className={`${
                    (variant == "light") ? "text-white" : "text-black"
                  } text-lg ${
                    (variant == "light")
                      ? "hover:text-gray-200"
                      : "hover:text-gray-700"
                  }`}
                >
                  {page.title}
                </a>
              </Link>
            );
          })}
        </div>
        <div className="absolute px-0 right-8  visible md:hidden">
          <button
            className={`${secondaryColor} p-1 mr-2 rounded-md`}
            onClick={() => setIsOpen(!isOpen)}
          >
            <FontAwesomeIcon
              size="lg"
              color={(variant == "light") ? "white" : "black"}
              icon={faBars}
            />
          </button>
        </div>
      </nav>
      {isOpen ? (
        <div className={`${primaryColor} flex flex-col space-y-2 md:hidden`}>
          {links.map((page, index) => {
            return (
              <Link key={index} href={page.address}>
                <a
                  className={`${
                    variant == "light" ? "text-white" : "text-black"
                  } text-lg ${
                    variant == "light"
                      ? "hover:text-gray-50"
                      : "hover:text-gray-800"
                  }`}
                >
                  <div className={`${secondaryColor} cursor-pointer pl-3`}>
                    {page.title}{" "}
                  </div>
                </a>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="hidden"> </div>
      )}
    </div>
  );
}

